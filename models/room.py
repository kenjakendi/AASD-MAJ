from typing import List, Optional
from datetime import datetime, time
from dataclasses import dataclass, field
from models.enums import RoomState, RoomType


@dataclass
class Room:
    room_id: str
    name: str
    room_type: RoomType
    capacity: int
    current_occupants: List[str] = field(default_factory=list)
    
    # Cleanliness
    cleanliness_state: RoomState = RoomState.CLEAN
    last_cleaned: Optional[datetime] = None
    
    # Cleaning schedule
    daily_clean_time: str = "08:00"  # HH:MM format
    clean_frequency_hours: int = 24
    
    # Special requirements
    requires_special_cleaning: bool = False
    special_cleaning_notes: str = ""
    
    def to_dict(self) -> dict:
        return {
            'id': self.room_id,
            'name': self.name,
            'type': self.room_type.value,
            'capacity': self.capacity,
            'current_occupants': self.current_occupants,
            'cleanliness_state': self.cleanliness_state.value,
            'last_cleaned': self.last_cleaned.isoformat() if self.last_cleaned else None,
            'daily_clean_time': self.daily_clean_time,
            'clean_frequency_hours': self.clean_frequency_hours,
            'requires_special_cleaning': self.requires_special_cleaning,
            'special_cleaning_notes': self.special_cleaning_notes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Room':
        return cls(
            room_id=data['id'],
            name=data['name'],
            room_type=RoomType(data.get('type', 'animal_housing')),
            capacity=data['capacity'],
            current_occupants=data.get('current_occupants', []),
            cleanliness_state=RoomState(data.get('cleanliness_state', 'clean')),
            last_cleaned=datetime.fromisoformat(data['last_cleaned']) if data.get('last_cleaned') else None,
            daily_clean_time=data.get('daily_clean_time', '08:00'),
            clean_frequency_hours=data.get('clean_frequency_hours', 24),
            requires_special_cleaning=data.get('requires_special_cleaning', False),
            special_cleaning_notes=data.get('special_cleaning_notes', '')
        )
    
    def needs_cleaning(self) -> bool:
        # If already dirty, needs cleaning
        if self.cleanliness_state == RoomState.DIRTY:
            return True
        
        # If never cleaned, needs cleaning
        if not self.last_cleaned:
            return True
        
        # Check if cleaning frequency exceeded
        elapsed_hours = (datetime.now() - self.last_cleaned).total_seconds() / 3600
        return elapsed_hours >= self.clean_frequency_hours
    
    def is_scheduled_for_cleaning(self) -> bool:
        now = datetime.now().time()
        try:
            clean_time = time.fromisoformat(self.daily_clean_time)
            # Within 30 minutes of scheduled time
            time_diff = abs((now.hour * 60 + now.minute) - 
                          (clean_time.hour * 60 + clean_time.minute))
            return time_diff <= 30
        except:
            return False
    
    def mark_dirty(self):
        self.cleanliness_state = RoomState.DIRTY
    
    def mark_cleaning_in_progress(self):
        self.cleanliness_state = RoomState.CLEANING_IN_PROGRESS
    
    def mark_clean(self):
        self.cleanliness_state = RoomState.CLEAN
        self.last_cleaned = datetime.now()
    
    def add_occupant(self, animal_id: str) -> bool:
        if len(self.current_occupants) >= self.capacity:
            return False
        if animal_id not in self.current_occupants:
            self.current_occupants.append(animal_id)
        return True
    
    def remove_occupant(self, animal_id: str):
        if animal_id in self.current_occupants:
            self.current_occupants.remove(animal_id)
    
    def is_full(self) -> bool:
        return len(self.current_occupants) >= self.capacity
    
    def is_empty(self) -> bool:
        return len(self.current_occupants) == 0
