from typing import Dict, Any, List, Set
from dataclasses import dataclass


@dataclass
class AvailabilityProtocol:
    
    # Protocol name
    NAME = "AvailabilityProtocol"
    
    # Message types
    UPDATE_WORKER_AVAILABILITY = "UpdateWorkerAvailability"
    CONFIRM_UPDATE_WORKER_AVAILABILITY = "ConfirmUpdateWorkerAvailability"
    
    @staticmethod
    def create_update(worker_id: str, is_available: bool, 
                     current_load: int, max_concurrent_tasks: int,
                     competencies: List[str]) -> Dict[str, Any]:
        return {
            'protocol': AvailabilityProtocol.UPDATE_WORKER_AVAILABILITY,
            'workerId': worker_id,
            'isAvailable': is_available,
            'currentLoad': current_load,
            'maxConcurrentTasks': max_concurrent_tasks,
            'competencies': competencies
        }
    
    @staticmethod
    def create_confirmation(worker_id: str, success: bool = True) -> Dict[str, Any]:
        return {
            'protocol': AvailabilityProtocol.CONFIRM_UPDATE_WORKER_AVAILABILITY,
            'workerId': worker_id,
            'success': success
        }
