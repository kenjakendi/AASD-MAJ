from typing import Dict, Any, Optional
from datetime import datetime
import json


class MessageBuilder:
    
    @staticmethod
    def build_request(protocol: str, content: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'type': 'request',
            'protocol': protocol,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def build_confirmation(protocol: str, task_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'type': 'confirm',
            'protocol': protocol,
            'taskId': task_id,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def build_inform(protocol: str, content: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'type': 'inform',
            'protocol': protocol,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def build_task_assignment(task_id: str, task_type: str, 
                             parameters: Dict[str, Any], 
                             priority: str = "normal") -> Dict[str, Any]:
        return {
            'taskId': task_id,
            'taskType': task_type,
            'parameters': parameters,
            'priority': priority,
            'assignedAt': datetime.now().isoformat()
        }
    
    @staticmethod
    def build_availability_update(worker_id: str, is_available: bool, 
                                  current_load: int, competencies: list) -> Dict[str, Any]:
        return {
            'workerId': worker_id,
            'isAvailable': is_available,
            'currentLoad': current_load,
            'competencies': competencies,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def build_error_message(error_type: str, message: str, 
                           context: Optional[Dict] = None) -> Dict[str, Any]:
        return {
            'type': 'error',
            'errorType': error_type,
            'message': message,
            'context': context or {},
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def serialize(data: Dict[str, Any]) -> str:
        return json.dumps(data, default=str, ensure_ascii=False)
    
    @staticmethod
    def deserialize(json_str: str) -> Dict[str, Any]:
        return json.loads(json_str)
