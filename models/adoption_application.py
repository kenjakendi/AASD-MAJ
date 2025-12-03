from typing import Dict, Optional
from datetime import datetime
from dataclasses import dataclass, field
from models.enums import ApplicationStatus


@dataclass
class AdoptionApplication:
    application_id: str
    applicant_id: str
    animal_id: str
    
    # Applicant information
    applicant_name: str
    applicant_age: int
    applicant_contact: str
    applicant_address: str
    
    # Application details
    has_previous_pet_experience: bool = False
    home_type: str = ""  # apartment, house, etc.
    has_yard: bool = False
    other_pets: list = field(default_factory=list)
    household_members: int = 1
    employment_status: str = ""
    
    # References
    references: list = field(default_factory=list)
    
    # Application status
    status: ApplicationStatus = ApplicationStatus.SUBMITTED
    submitted_at: datetime = field(default_factory=datetime.now)
    reviewed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Review
    reviewer_notes: str = ""
    rejection_reason: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'application_id': self.application_id,
            'applicant_id': self.applicant_id,
            'animal_id': self.animal_id,
            'applicant_name': self.applicant_name,
            'applicant_age': self.applicant_age,
            'applicant_contact': self.applicant_contact,
            'applicant_address': self.applicant_address,
            'has_previous_pet_experience': self.has_previous_pet_experience,
            'home_type': self.home_type,
            'has_yard': self.has_yard,
            'other_pets': self.other_pets,
            'household_members': self.household_members,
            'employment_status': self.employment_status,
            'references': self.references,
            'status': self.status.value,
            'submitted_at': self.submitted_at.isoformat(),
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'reviewer_notes': self.reviewer_notes,
            'rejection_reason': self.rejection_reason
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AdoptionApplication':
        return cls(
            application_id=data['application_id'],
            applicant_id=data['applicant_id'],
            animal_id=data['animal_id'],
            applicant_name=data['applicant_name'],
            applicant_age=data['applicant_age'],
            applicant_contact=data['applicant_contact'],
            applicant_address=data['applicant_address'],
            has_previous_pet_experience=data.get('has_previous_pet_experience', False),
            home_type=data.get('home_type', ''),
            has_yard=data.get('has_yard', False),
            other_pets=data.get('other_pets', []),
            household_members=data.get('household_members', 1),
            employment_status=data.get('employment_status', ''),
            references=data.get('references', []),
            status=ApplicationStatus(data.get('status', 'submitted')),
            submitted_at=datetime.fromisoformat(data['submitted_at']) if data.get('submitted_at') else datetime.now(),
            reviewed_at=datetime.fromisoformat(data['reviewed_at']) if data.get('reviewed_at') else None,
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
            reviewer_notes=data.get('reviewer_notes', ''),
            rejection_reason=data.get('rejection_reason', '')
        )
    
    def approve(self, notes: str = ""):
        self.status = ApplicationStatus.APPROVED
        self.reviewed_at = datetime.now()
        self.reviewer_notes = notes
    
    def reject(self, reason: str):
        self.status = ApplicationStatus.REJECTED
        self.reviewed_at = datetime.now()
        self.rejection_reason = reason
    
    def complete(self):
        self.status = ApplicationStatus.COMPLETED
        self.completed_at = datetime.now()
    
    def start_review(self):
        self.status = ApplicationStatus.UNDER_REVIEW
        self.reviewed_at = datetime.now()
