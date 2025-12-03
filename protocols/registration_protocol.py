from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class RegistrationProtocol:
    
    # Protocol name
    NAME = "RegistrationProtocol"
    
    # Message types
    REGISTER_NEW_ANIMAL = "RegisterNewAnimal"
    ASSIGN_INITIAL_CHECKUP_TASK = "AssignInitialCheckupTask"
    CONFIRM_INITIAL_CHECKUP_TASK = "ConfirmInitialCheckupTask"
    
    @staticmethod
    def create_registration(animal_id: str, animal_data: Dict[str, Any],
                          quarantine_room_id: str = None) -> Dict[str, Any]:
        return {
            'protocol': RegistrationProtocol.REGISTER_NEW_ANIMAL,
            'animalId': animal_id,
            'quarantineRoomId': quarantine_room_id,
            **animal_data
        }
    
    @staticmethod
    def create_checkup_assignment(task_id: str, animal_id: str, 
                                 animal_name: str, worker_id: str) -> Dict[str, Any]:
        return {
            'protocol': RegistrationProtocol.ASSIGN_INITIAL_CHECKUP_TASK,
            'taskId': task_id,
            'animalId': animal_id,
            'animalName': animal_name,
            'workerId': worker_id,
            'isNewArrival': True
        }
    
    @staticmethod
    def create_checkup_confirmation(task_id: str, animal_id: str, 
                                   worker_id: str, health_status: str = "healthy",
                                   clear_for_adoption: bool = True,
                                   success: bool = True) -> Dict[str, Any]:
        return {
            'protocol': RegistrationProtocol.CONFIRM_INITIAL_CHECKUP_TASK,
            'taskId': task_id,
            'animalId': animal_id,
            'workerId': worker_id,
            'healthStatus': health_status,
            'clearForAdoption': clear_for_adoption,
            'success': success,
            'newState': health_status
        }
