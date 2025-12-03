from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class FeedProtocol:
    
    # Protocol name
    NAME = "FeedProtocol"
    
    # Message types
    FEED_REQUEST = "FeedRequest"
    ASSIGN_FEED_TASK = "AssignFeedTask"
    CONFIRM_FEED_TASK = "ConfirmFeedTask"
    
    @staticmethod
    def create_request(animal_id: str, animal_name: str, 
                      dietary_requirements: str = "standard") -> Dict[str, Any]:
        return {
            'protocol': FeedProtocol.FEED_REQUEST,
            'animalId': animal_id,
            'animalName': animal_name,
            'dietaryRequirements': dietary_requirements
        }
    
    @staticmethod
    def create_assignment(task_id: str, animal_id: str, 
                         animal_name: str, worker_id: str) -> Dict[str, Any]:
        return {
            'protocol': FeedProtocol.ASSIGN_FEED_TASK,
            'taskId': task_id,
            'animalId': animal_id,
            'animalName': animal_name,
            'workerId': worker_id
        }
    
    @staticmethod
    def create_confirmation(task_id: str, animal_id: str, 
                          worker_id: str, success: bool = True) -> Dict[str, Any]:
        return {
            'protocol': FeedProtocol.CONFIRM_FEED_TASK,
            'taskId': task_id,
            'animalId': animal_id,
            'workerId': worker_id,
            'success': success,
            'newState': 'fed' if success else 'hungry'
        }
