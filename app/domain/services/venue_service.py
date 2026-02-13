"""Service for managing venues."""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.models.venue import Venue, VenueType

class VenueService:
    @staticmethod
    def get_all(db: Session) -> List[Venue]:
        """Retrieve all venues."""
        return db.query(Venue).all()

    @staticmethod
    def get_by_id(db: Session, venue_id: str) -> Optional[Venue]:
        """Retrieve a venue by ID."""
        return db.query(Venue).filter(Venue.id == venue_id).first()

    @staticmethod
    def create(db: Session, name: str, capacity: int, type: str) -> Venue:
        """Create a new venue."""
        # Convert string type to Enum
        try:
            venue_type = VenueType(type.lower()) # Assuming values match enum values e.g. "lecture_hall"
            # If values from form are "Lecture Hall", we might need mapping.
            # Base on select options: "Lecture Hall" -> expected enum value "lecture_hall" ?
            # Let's check model enum values: LECTURE_HALL = "lecture_hall"
        except ValueError:
            # Fallback or mapping logic
            type_map = {
                "Lecture Hall": "lecture_hall",
                "Lab": "lab",
                "Classroom": "classroom"
            }
            mapped_val = type_map.get(type, "classroom")
            venue_type = VenueType(mapped_val)

        new_venue = Venue(
            name=name,
            capacity=capacity,
            type=venue_type
        )
        db.add(new_venue)
        db.commit()
        db.refresh(new_venue)
        return new_venue

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Venue]:
        """Retrieve a venue by name."""
        return db.query(Venue).filter(Venue.name == name).first()

    @staticmethod
    def update(db: Session, name: str, capacity: int, type: str) -> Optional[Venue]:
        """Update an existing venue."""
        venue = db.query(Venue).filter(Venue.name == name).first()
        
        # Convert string type to Enum
        try:
            # Simple direct mapping first
            venue_type = VenueType(type.lower()) 
        except ValueError:
             # Fallback
            type_map = {
                "Lecture Hall": "lecture_hall",
                "Lab": "lab",
                "Classroom": "classroom"
            }
            mapped_val = type_map.get(type, "classroom")
            venue_type = VenueType(mapped_val)

        if venue:
            venue.capacity = capacity
            venue.type = venue_type
            db.commit()
            db.refresh(venue)
            return venue
        return None

    @staticmethod
    def delete(db: Session, venue_id: str) -> bool:
        """Delete a venue by ID."""
        venue = db.query(Venue).filter(Venue.id == venue_id).first()
        if venue:
            db.delete(venue)
            db.commit()
            return True
        return False
