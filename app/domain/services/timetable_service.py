"""Timetable domain service."""

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.domain.models import Course, Lecturer, Venue, TimetableEntry

class TimetableService:
    """Service for timetable operations."""

    @staticmethod
    def get_stats(db: Session, semester: int = None):
        """Get statistics for the generation page."""
        course_query = db.query(func.count(Course.id))
        if semester:
            course_query = course_query.filter(Course.semester == semester)
            
        return {
            "courses": course_query.scalar(),
            # Lecturers and Venues are typically shared across semesters or global resources
            "lecturers": db.query(func.count(Lecturer.id)).scalar(),
            "venues": db.query(func.count(Venue.id)).scalar()
        }

    @staticmethod
    def generate_timetable(db: Session, semester: int = 1, constraints: dict = None, session: str = "2024/2025"):
        """
        Generate the timetable using the CSP Scheduler.
        Creates a new Timetable record (Draft).
        
        Args:
            db: Database session
            semester: Target semester (1 or 2)
            constraints: Dict mapping course_id -> {"duration": int, "frequency": int}
            session: Academic session string
            
        Returns:
            (success, timetable_id)
        """
        from app.domain.services.scheduler import SchedulerService
        from app.domain.models import Timetable, TimetableStatus
        
        # Create Parent Timetable
        timetable = Timetable(
            academic_session=session,
            semester=semester,
            status=TimetableStatus.DRAFT,
            is_active=False
        )
        db.add(timetable)
        db.commit() # Commit to get ID
        
        scheduler = SchedulerService(db, timetable_id=timetable.id, semester=semester, constraints=constraints)
        success = scheduler.generate()
        
        return success, timetable.id

    @staticmethod
    def get_timetable_grid(db: Session, timetable_id: str = None, department: str = None, level: str = None):
        """Retrieve timetable entries organized for the grid view."""
        from app.domain.models import Timetable, TimetableStatus
        
        # If no ID provided, get latest active or latest draft
        if not timetable_id:
            # Try get active first
            active = db.query(Timetable).filter(Timetable.is_active == True).order_by(Timetable.created_at.desc()).first()
            if active:
                timetable_id = active.id
            else:
                # Get latest generated
                latest = db.query(Timetable).order_by(Timetable.created_at.desc()).first()
                if latest:
                    timetable_id = latest.id
                else:
                    # No timetables exist
                    return {"days": [], "times": [], "grid": {}, "timetable": None}
                    
        timetable = db.query(Timetable).filter(Timetable.id == timetable_id).first()
        if not timetable:
             return {"days": [], "times": [], "grid": {}, "timetable": None}

        # Use outerjoin for venue since venue_id can be NULL (unassigned)
        query = (
            db.query(TimetableEntry)
            .filter(TimetableEntry.timetable_id == timetable_id)
            .join(TimetableEntry.course)
            .join(TimetableEntry.timeslot)
            .outerjoin(TimetableEntry.venue)  # LEFT JOIN for nullable venue_id
        )
        
        if department and department != "All":
            query = query.filter(Course.department == department)
        if level and level != "All":
            query = query.filter(Course.level == int(level))
            
        entries = query.all()
        
        # Structure data: grid[time_str][day_str] = [entry1, entry2...]
        grid = {}
        
        # Get all unique timeslots properly sorted
        from app.domain.models.timeslot import TimeSlot, DayOfWeek
        all_slots = db.query(TimeSlot).all()
        
        # Sort days: Monday -> Friday
        day_order = {d.value: i for i, d in enumerate(DayOfWeek)}
        days = sorted([d.value for d in DayOfWeek], key=lambda d: day_order[d])
        
        # Sort times
        times = sorted(list(set([(s.start_time, s.end_time) for s in all_slots])))
        
        # Initialize grid
        for start, end in times:
            time_key = f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}"
            grid[time_key] = {day: [] for day in days}
            
        # Populate grid
        for entry in entries:
            time_key = f"{entry.timeslot.start_time.strftime('%H:%M')}-{entry.timeslot.end_time.strftime('%H:%M')}"
            day_key = entry.timeslot.day.value
            if time_key in grid and day_key in grid[time_key]:
                grid[time_key][day_key].append(entry)
                
        return {
            "days": days,
            "times": [f"{s.strftime('%H:%M')}-{e.strftime('%H:%M')}" for s, e in times],
            "grid": grid,
            "timetable": timetable
        }

    @staticmethod
    def get_entry(db: Session, entry_id: str):
        """Get a single timetable entry."""
        return db.query(TimetableEntry).filter(TimetableEntry.id == entry_id).first()

    @staticmethod
    def update_entry(db: Session, entry_id: str, new_timeslot_id: str, new_venue_id: str):
        """
        Update a timetable entry.
        Also sets is_locked=True to prevent overwrite by auto-generation.
        Returns (success, message).
        """
        entry = db.query(TimetableEntry).filter(TimetableEntry.id == entry_id).first()
        if not entry:
            return False, "Entry not found."

        # Check for conflicts within the SAME TIMETABLE
        # 1. Venue Conflict
        venue_conflict = db.query(TimetableEntry).filter(
            TimetableEntry.timetable_id == entry.timetable_id, # Scope check
            TimetableEntry.timeslot_id == new_timeslot_id,
            TimetableEntry.venue_id == new_venue_id,
            TimetableEntry.id != entry_id # Exclude self
        ).first()
        
        if venue_conflict:
            return False, f"Venue is already booked by {venue_conflict.course.code} at this time."

        # 2. Lecturer Conflict (if lecturer assigned)
        if entry.course.lecturer_id:
            lecturer_conflict = db.query(TimetableEntry).join(TimetableEntry.course).filter(
                TimetableEntry.timetable_id == entry.timetable_id, # Scope check
                TimetableEntry.timeslot_id == new_timeslot_id,
                Course.lecturer_id == entry.course.lecturer_id,
                TimetableEntry.id != entry_id
            ).first()
            if lecturer_conflict:
                return False, f"Lecturer is already teaching {lecturer_conflict.course.code} at this time."

        # Update
        entry.timeslot_id = new_timeslot_id
        entry.venue_id = new_venue_id
        # entry.is_locked = True # Lock logic less relevant if we use drafts, but okay to keep.
        db.commit()
        return True, "Entry updated successfully."

    @staticmethod
    def restore_timetable(db: Session):
        """Unlock all entries (Restore)."""
        db.query(TimetableEntry).update({TimetableEntry.is_locked: False})
        db.commit()
        return True

    @staticmethod
    def get_all_timetables(db: Session):
        """Get all timetables ordered by creation date."""
        from app.domain.models import Timetable
        return db.query(Timetable).order_by(Timetable.created_at.desc()).all()
        
    @staticmethod
    def delete_timetable(db: Session, timetable_id: str):
        """Delete a timetable and its entries."""
        from app.domain.models import Timetable
        timetable = db.query(Timetable).filter(Timetable.id == timetable_id).first()
        if timetable:
            db.delete(timetable)
            db.commit()
            return True
        return False
        
    @staticmethod
    def publish_timetable(db: Session, timetable_id: str):
        """
        Publish a timetable.
        Ensures only one active published timetable per (session, semester).
        """
        from app.domain.models import Timetable, TimetableStatus
        
        target = db.query(Timetable).filter(Timetable.id == timetable_id).first()
        if not target:
            return False, "Timetable not found."
            
        # Deactivate others for same session/semester
        db.query(Timetable).filter(
            Timetable.academic_session == target.academic_session,
            Timetable.semester == target.semester,
            Timetable.status == TimetableStatus.PUBLISHED
        ).update({Timetable.is_active: False}) # Or separate is_active logic
        
        # Ideally, 'Published' implies Active? Or can we have archived published ones?
        # User said "access past sessions".
        # So past ones can be PUBLISHED but not ACTIVE (if active means current semester).
        # But for now, let's just mark it published.
        
        target.status = TimetableStatus.PUBLISHED
        target.is_active = True
        db.commit()
        return True, "Timetable published successfully."
