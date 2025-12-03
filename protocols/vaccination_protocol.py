from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class VaccinationProtocol:
    
    # Protocol name
    NAME = "VaccinationProtocol"
    
    # Message types
    ASSIGN_VACCINATION_TASK = "AssignVaccinationTask"
    CONFIRM_VACCINATION_TASK = "ConfirmVaccinationTask"
    
    @staticmethod
    def create_assignment(task_id: str, animal_id: str, 
                         animal_name: str, worker_id: str,
                         vaccination_type: str = "routine") -> Dict[str, Any]:
        return {
            'protocol': VaccinationProtocol.ASSIGN_VACCINATION_TASK,
            'taskId': task_id,
            'animalId': animal_id,
            'animalName': animal_name,
            'workerId': worker_id,
            'vaccinationType': vaccination_type
        }
    
    @staticmethod
    def create_confirmation(task_id: str, animal_id: str, 
                          worker_id: str, vaccination_type: str,
                          success: bool = True) -> Dict[str, Any]:
        return {
            'protocol': VaccinationProtocol.CONFIRM_VACCINATION_TASK,
            'taskId': task_id,
            'animalId': animal_id,
            'workerId': worker_id,
            'vaccinationType': vaccination_type,
            'success': success,
            'vaccinated': success
        }
