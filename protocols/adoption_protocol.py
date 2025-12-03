from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class AdoptionProtocol:
    
    # Protocol name
    NAME = "AdoptionProtocol"
    
    # Message types
    ADOPTION_APPLICATION_REQUEST = "AdoptionApplicationRequest"
    ADOPTION_APPLICATION_TASK = "AdoptionApplicationTask"
    CONFIRM_ADOPTION_APPLICATION_TASK = "ConfirmAdoptionApplicationTask"
    
    @staticmethod
    def create_request(application_id: str, applicant_id: str, 
                      animal_id: str, applicant_info: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'protocol': AdoptionProtocol.ADOPTION_APPLICATION_REQUEST,
            'applicationId': application_id,
            'applicantId': applicant_id,
            'animalId': animal_id,
            **applicant_info
        }
    
    @staticmethod
    def create_assignment(application_id: str, animal_id: str, 
                         applicant_id: str) -> Dict[str, Any]:
        return {
            'protocol': AdoptionProtocol.ADOPTION_APPLICATION_TASK,
            'applicationId': application_id,
            'animalId': animal_id,
            'applicantId': applicant_id
        }
    
    @staticmethod
    def create_confirmation(application_id: str, animal_id: str, 
                          applicant_id: str, status: str = "approved",
                          success: bool = True) -> Dict[str, Any]:
        return {
            'protocol': AdoptionProtocol.CONFIRM_ADOPTION_APPLICATION_TASK,
            'applicationId': application_id,
            'animalId': animal_id,
            'applicantId': applicant_id,
            'status': status,
            'success': success,
            'adoptionStatus': 'adopted' if success and status == 'approved' else 'available'
        }
