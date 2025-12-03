from typing import Dict, List, Optional
from datetime import datetime, date
from dataclasses import dataclass, field
from models.enums import AnimalHealthStatus, AnimalAdoptionStatus


@dataclass
class Animal:
    animal_id: str
    name: str
    species: str
    breed: str
    age: int
    sex: str
    
    # Health information
    health_status: AnimalHealthStatus = AnimalHealthStatus.HEALTHY
    vaccination_status: Dict[str, str] = field(default_factory=dict)
    next_vaccination_due: Optional[str] = None
    medications: List[str] = field(default_factory=list)
    
    # Care requirements
    dietary_requirements: str = "standard"
    behavioral_notes: str = ""
    
    # Adoption information
    adoption_status: AnimalAdoptionStatus = AnimalAdoptionStatus.AVAILABLE
    
    # State tracking
    last_fed: Optional[datetime] = None
    last_walked: Optional[datetime] = None
    last_health_check: Optional[datetime] = None
    
    # Metadata
    intake_date: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.animal_id,
            'name': self.name,
            'species': self.species,
            'breed': self.breed,
            'age': self.age,
            'sex': self.sex,
            'health_status': self.health_status.value,
            'vaccination_status': self.vaccination_status,
            'next_vaccination_due': self.next_vaccination_due,
            'medications': self.medications,
            'dietary_requirements': self.dietary_requirements,
            'behavioral_notes': self.behavioral_notes,
            'adoption_status': self.adoption_status.value,
            'last_fed': self.last_fed.isoformat() if self.last_fed else None,
            'last_walked': self.last_walked.isoformat() if self.last_walked else None,
            'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None,
            'intake_date': self.intake_date.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Animal':
        return cls(
            animal_id=data['id'],
            name=data['name'],
            species=data['species'],
            breed=data['breed'],
            age=data['age'],
            sex=data['sex'],
            health_status=AnimalHealthStatus(data.get('health_status', 'healthy')),
            vaccination_status=data.get('vaccination_status', {}),
            next_vaccination_due=data.get('next_vaccination_due'),
            medications=data.get('medications', []),
            dietary_requirements=data.get('dietary_requirements', 'standard'),
            behavioral_notes=data.get('behavioral_notes', ''),
            adoption_status=AnimalAdoptionStatus(data.get('adoption_status', 'available')),
            last_fed=datetime.fromisoformat(data['last_fed']) if data.get('last_fed') else None,
            last_walked=datetime.fromisoformat(data['last_walked']) if data.get('last_walked') else None,
            last_health_check=datetime.fromisoformat(data['last_health_check']) if data.get('last_health_check') else None,
            intake_date=datetime.fromisoformat(data['intake_date']) if data.get('intake_date') else datetime.now()
        )
    
    def needs_feeding(self, interval_hours: int = 8) -> bool:
        if not self.last_fed:
            return True
        elapsed = (datetime.now() - self.last_fed).total_seconds() / 3600
        return elapsed >= interval_hours
    
    def needs_walk(self, interval_hours: int = 6) -> bool:
        if self.species.lower() != 'dog':
            return False
        if not self.last_walked:
            return True
        elapsed = (datetime.now() - self.last_walked).total_seconds() / 3600
        return elapsed >= interval_hours
    
    def needs_health_check(self) -> bool:
        if self.health_status in [AnimalHealthStatus.SICK, AnimalHealthStatus.NEEDS_CHECKUP]:
            return True
        if not self.last_health_check:
            return True
        elapsed = (datetime.now() - self.last_health_check).total_seconds() / 86400  # days
        return elapsed >= 30  # Monthly health check
    
    def needs_vaccination(self) -> bool:
        if not self.next_vaccination_due:
            return False
        try:
            due_date = datetime.strptime(self.next_vaccination_due, '%Y-%m-%d').date()
            return date.today() >= due_date
        except:
            return False
    
    def update_feed_state(self):
        self.last_fed = datetime.now()
    
    def update_walk_state(self):
        self.last_walked = datetime.now()
    
    def update_health_status(self, status: AnimalHealthStatus):
        self.health_status = status
        self.last_health_check = datetime.now()
