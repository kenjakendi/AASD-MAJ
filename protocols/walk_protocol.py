from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class WalkProtocol:
    
    # Protocol name
    NAME = "WalkProtocol"
    
    # Message types
    WALK_REQUEST = "WalkRequest"
    ASSIGN_WALK_TASK = "AssignWalkTask"
    CONFIRM_WALK_TASK = "ConfirmWalkTask"
    
    @staticmethod
    def create_request(animal_id: str, animal_name: str, 
                      behavioral_notes: str = "") -> Dict[str, Any]:
        return {
            'protocol': WalkProtocol.WALK_REQUEST,
            'animalId': animal_id,
            'animalName': animal_name,
            'behavioralNotes': behavioral_notes
        }
    
    @staticmethod
    def create_assignment(task_id: str, animal_id: str, 
                         animal_name: str, worker_id: str) -> Dict[str, Any]:
        return {
            'protocol': WalkProtocol.ASSIGN_WALK_TASK,
            'taskId': task_id,
            'animalId': animal_id,
            'animalName': animal_name,
            'workerId': worker_id
        }
    
    @staticmethod
    def create_confirmation(task_id: str, animal_id: str, 
                          worker_id: str, success: bool = True) -> Dict[str, Any]:
        return {
            'protocol': WalkProtocol.CONFIRM_WALK_TASK,
            'taskId': task_id,
            'animalId': animal_id,
            'workerId': worker_id,
            'success': success,
            'newState': 'walked' if success else 'needsWalk'
        }
