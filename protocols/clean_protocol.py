from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class CleanProtocol:
    
    # Protocol name
    NAME = "CleanProtocol"
    
    # Message types
    CLEAN_REQUEST = "CleanRequest"
    ASSIGN_CLEAN_TASK = "AssignCleanTask"
    CONFIRM_CLEAN_TASK = "ConfirmCleanTask"
    
    @staticmethod
    def create_request(room_id: str, room_name: str, 
                      requires_special_cleaning: bool = False,
                      special_notes: str = "") -> Dict[str, Any]:
        return {
            'protocol': CleanProtocol.CLEAN_REQUEST,
            'roomId': room_id,
            'roomName': room_name,
            'requiresSpecialCleaning': requires_special_cleaning,
            'specialNotes': special_notes
        }
    
    @staticmethod
    def create_assignment(task_id: str, room_id: str, 
                         room_name: str, worker_id: str,
                         requires_special_cleaning: bool = False) -> Dict[str, Any]:
        return {
            'protocol': CleanProtocol.ASSIGN_CLEAN_TASK,
            'taskId': task_id,
            'roomId': room_id,
            'roomName': room_name,
            'workerId': worker_id,
            'requiresSpecialCleaning': requires_special_cleaning
        }
    
    @staticmethod
    def create_confirmation(task_id: str, room_id: str, 
                          worker_id: str, success: bool = True) -> Dict[str, Any]:
        return {
            'protocol': CleanProtocol.CONFIRM_CLEAN_TASK,
            'taskId': task_id,
            'roomId': room_id,
            'workerId': worker_id,
            'success': success,
            'newState': 'clean' if success else 'dirty'
        }
