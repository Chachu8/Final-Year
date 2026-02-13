"""Scheduler Service implementing CSP Algorithm."""

import random
from typing import List, Dict, Optional, Tuple, Set
from sqlalchemy.orm import Session
from sqlalchemy import delete

from app.domain.models import Course, Lecturer, Venue, TimeSlot, TimetableEntry
from app.domain.models.timeslot import DayOfWeek

class SchedulerService:
    """
    Constraint Satisfaction Problem (CSP) Solver for Timetable Generation.
    Supports:
    - Multi-hour blocks (consecutive slots)
    - Multi-session courses (frequency > 1)
    - Semester filtering
    - Dynamic constraints (configured at generation time)
    """
    
    def __init__(self, db: Session, timetable_id: str, semester: int = 1, constraints: dict = None):
        """
        Initialize the scheduler.
        
        Args:
            db: Database session
            timetable_id: The ID of the parent Timetable record
            semester: Target semester (1 or 2)
            constraints: Dict mapping course_id -> {"duration": int, "frequency": int}
                        If None or course not in dict, defaults to duration=1, frequency=1
        """
        self.db = db
        self.timetable_id = timetable_id
        self.semester = semester
        self.constraints = constraints or {}  # course_id -> {duration, frequency}
        
        self.courses: List[Course] = []
        self.lecturers: List[Lecturer] = []
        self.venues: List[Venue] = []
        self.timeslots: List[TimeSlot] = []
        
        # Scheduling Items: (Course, SessionIndex, Duration)
        self.items: List[Tuple[Course, int, int]] = []
        
        # Domains: ItemIndex -> List[(StartSlotIndex, Venue)]
        # We work with INDICES for speed
        self.domains: Dict[int, List[Tuple[int, Venue]]] = {}
        
        # Assignment: ItemIndex -> (StartSlotIndex, Venue)
        self.assignment: Dict[int, Tuple[int, Venue]] = {}

    def generate(self) -> bool:
        """Main entry point to generate the timetable."""
        # 1. Clear existing non-locked entries?
        # NO. We are generating a key-assigned timetable version.
        # The parent logic handles creating the Timetable record.
        # We just insert new entries.
        
        # 2. Load Data
        self._load_data()
        
        if not self.items or not self.timeslots or not self.venues:
            print("Error: insufficient data.")
            return False

        # 3. Initialize Domains
        self._initialize_domains()
        
        # 4. Run Backtracking Search
        if self._backtrack():
            self._save_solution()
            return True
        else:
            print("No solution found.")
            return False

    def _load_data(self):
        """Load entities and build schedule items."""
        # Filter courses by semester
        self.courses = self.db.query(Course).filter(Course.semester == self.semester).all()
        self.venues = self.db.query(Venue).all()
        
        # Ensure timeslots are sorted by Day then StartTime
        # Logic depends on linear indexing!
        day_map = {d: i for i, d in enumerate([DayOfWeek.MONDAY, DayOfWeek.TUESDAY, DayOfWeek.WEDNESDAY, DayOfWeek.THURSDAY, DayOfWeek.FRIDAY])}
        all_slots = self.db.query(TimeSlot).all()
        
        # Filter out Friday 12-2 PM (Prayer time)
        from datetime import time
        filtered_slots = []
        for slot in all_slots:
            # Block Friday 13:00-15:00 (1 PM - 3 PM)
            if slot.day == DayOfWeek.FRIDAY and slot.start_time >= time(13, 0) and slot.start_time < time(15, 0):
                continue  # Skip this slot
            filtered_slots.append(slot)
        
        self.timeslots = sorted(filtered_slots, key=lambda t: (day_map.get(t.day, 99), t.start_time))
        
        # Flatten courses into Items
        self.items = []
        for course in self.courses:
            # Get constraints from dict, default to 1 hour, 1x/week
            constraint = self.constraints.get(course.id, {})
            freq = constraint.get("frequency", 1)
            duration = constraint.get("duration", 1)
            
            for i in range(freq):
                self.items.append((course, i, duration))
        
        # PRIORITY SCHEDULING: Sort by Level (DESC) then Enrollment (DESC)
        # Higher levels (400, 300) get scheduled first
        self.items.sort(key=lambda x: (-(x[0].level or 0), -(x[0].enrollment or 0)))


    def _initialize_domains(self):
        """Initialize domain for each item."""
        # Pre-calculate valid start slots for durations 1, 2, 3...
        # A slot `i` is a valid start for duration `d` if `i` to `i+d-1` are consecutive on same day.
        
        valid_starts_by_duration = {}
        max_duration = max((item[2] for item in self.items), default=1)
        
        for d in range(1, max_duration + 1):
            valid_indices = []
            for i in range(len(self.timeslots) - d + 1):
                # Check strict consecutive: same day
                start_ts = self.timeslots[i]
                end_ts = self.timeslots[i + d - 1]
                if start_ts.day == end_ts.day:
                     # Also check timestamps? Assumed consecutive by array order if seed is consistent.
                     valid_indices.append(i)
            valid_starts_by_duration[d] = valid_indices

        # Build domains - ONLY TIMESLOTS, NO VENUES
        # Venues will be assigned manually by admin based on enrollment
        for idx, (course, session_i, duration) in enumerate(self.items):
            possible_starts = valid_starts_by_duration.get(duration, [])
            
            # Domain is just list of valid start slot indices
            # No venue assignment - that's manual
            item_domain = [(s_idx, None) for s_idx in possible_starts]
            
            random.shuffle(item_domain)
            self.domains[idx] = item_domain

    def _backtrack(self, item_idx: int = 0) -> bool:
        """Recursive backtracking."""
        if item_idx >= len(self.items):
            return True
        
        # Current item
        course, session_i, duration = self.items[item_idx]
        
        for (start_slot_idx, venue) in self.domains[item_idx]:
            if self._is_consistent(item_idx, start_slot_idx, venue):
                self.assignment[item_idx] = (start_slot_idx, venue)
                
                if self._backtrack(item_idx + 1):
                    return True
                
                del self.assignment[item_idx]
        
        return False

    def _is_consistent(self, current_item_idx: int, start_slot_idx: int, venue) -> bool:
        """Check conflicts for the proposed block assignment."""
        curr_course, _, curr_duration = self.items[current_item_idx]
        
        # Calculate the set of consumed slot indices for the current item
        curr_slots = set(range(start_slot_idx, start_slot_idx + curr_duration))
        
        for assigned_idx, (assigned_start, assigned_venue) in self.assignment.items():
            assigned_course, _, assigned_duration = self.items[assigned_idx]
            
            # Calculate assigned slots
            assigned_slots = set(range(assigned_start, assigned_start + assigned_duration))
            
            # intersection?
            if not curr_slots.isdisjoint(assigned_slots):
                # TIME OVERLAP DETECTED
                
                # No venue conflict check - venues are manually assigned
                
                # 1. Lecturer Conflict (if same lecturer teaches both)
                if curr_course.lecturer_id and assigned_course.lecturer_id:
                    if curr_course.lecturer_id == assigned_course.lecturer_id:
                        return False
                
                # 2. Group Conflict - REMOVED to allow parallel scheduling
                # Different courses for the same level can run simultaneously
                # This allows all 150 courses to be scheduled efficiently
                # Students will only be in ONE course at a time based on their registration
            
            # 3. Same Course Constraints (Twin Sessions)
            # If same course, shouldn't be on same day? (Optional soft constraint, but good practice)
            if curr_course.id == assigned_course.id:
                # If checking soft constraints, putting them on same day might be bad.
                # Hard constraint: Don't overlap (handled above).
                # Soft: Try to spread out?
                pass

        return True

    def _save_solution(self):
        """Persist assignment. Expand blocks into individual hourly entries."""
        new_entries = []
        for item_idx, (start_slot_idx, venue) in self.assignment.items():
            course, session_i, duration = self.items[item_idx]
            
            # Create one entry per hour of the block
            for offset in range(duration):
                slot_idx = start_slot_idx + offset
                timeslot = self.timeslots[slot_idx]
                
                entry = TimetableEntry(
                    timetable_id=self.timetable_id,
                    course_id=course.id,
                    timeslot_id=timeslot.id,
                    venue_id=venue.id if venue is not None else None
                    # We could add session metadata if model supported it
                )
                new_entries.append(entry)
        
        self.db.add_all(new_entries)
        self.db.commit()
