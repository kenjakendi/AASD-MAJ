from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class HealthProtocol:
    
    # Protocol name
    NAME = "HealthProtocol"
    
    # Message types
    HEALTH_REQUEST = "HealthRequest"
    HEALTH_REQUEST_TASK = "HealthRequestTask"
    CONFIRM_HEALTH_REQUEST_TASK = "ConfirmHealthRequestTask"
    
    @staticmethod
    def create_request(animal_id: str, animal_name: str, 
                      health_status: str = "unknown",
                      medications: List[str] = None) -> Dict[str, Any]:
        return {
            'protocol': HealthProtocol.HEALTH_REQUEST,
            'animalId': animal_id,
            'animalName': animal_name,
            'healthStatus': health_status,
            'medications': medications or []
        }
    
    @staticmethod
    def create_assignment(task_id: str, animal_id: str, 
                         animal_name: str, worker_id: str) -> Dict[str, Any]:
        return {
            'protocol': HealthProtocol.HEALTH_REQUEST_TASK,
            'taskId': task_id,
            'animalId': animal_id,
            'animalName': animal_name,
            'workerId': worker_id
        }
    
    @staticmethod
    def create_confirmation(task_id: str, animal_id: str, 
                          worker_id: str, health_status: str = "healthy",
                          success: bool = True) -> Dict[str, Any]:
        return {
            'protocol': HealthProtocol.CONFIRM_HEALTH_REQUEST_TASK,
            'taskId': task_id,
            'animalId': animal_id,
            'workerId': worker_id,
            'success': success,
            'newState': health_status
        }
