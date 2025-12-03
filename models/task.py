from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from models.enums import TaskStatus, TaskType, Priority


@dataclass
class Task:
    task_id: str
    task_type: TaskType
    priority: Priority
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    
    # Assignment
    assigned_to: Optional[str] = None
    assigned_at: Optional[datetime] = None
    
    # Lifecycle timestamps
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results and metadata
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    attempts: int = 0
    max_attempts: int = 3
    
    # Protocol information
    requester_jid: Optional[str] = None
    protocol_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'task_id': self.task_id,
            'task_type': self.task_type.value,
            'priority': self.priority.value,
            'parameters': self.parameters,
            'status': self.status.value,
            'assigned_to': self.assigned_to,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'result': self.result,
            'error_message': self.error_message,
            'attempts': self.attempts,
            'requester_jid': self.requester_jid,
            'protocol_name': self.protocol_name
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        return cls(
            task_id=data['task_id'],
            task_type=TaskType(data['task_type']),
            priority=Priority(data['priority']),
            parameters=data.get('parameters', {}),
            status=TaskStatus(data.get('status', 'pending')),
            assigned_to=data.get('assigned_to'),
            assigned_at=datetime.fromisoformat(data['assigned_at']) if data.get('assigned_at') else None,
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            started_at=datetime.fromisoformat(data['started_at']) if data.get('started_at') else None,
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
            result=data.get('result'),
            error_message=data.get('error_message'),
            attempts=data.get('attempts', 0),
            requester_jid=data.get('requester_jid'),
            protocol_name=data.get('protocol_name')
        )
    
    def can_retry(self) -> bool:
        return self.attempts < self.max_attempts
    
    def is_overdue(self, timeout_seconds: int = 300) -> bool:
        if self.started_at and not self.completed_at:
            elapsed = (datetime.now() - self.started_at).total_seconds()
            return elapsed > timeout_seconds
        return False
    
    def assign(self, worker_id: str):
        self.assigned_to = worker_id
        self.assigned_at = datetime.now()
        self.status = TaskStatus.ASSIGNED
        self.attempts += 1
    
    def start(self):
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()
    
    def complete(self, result: Dict[str, Any]):
        self.status = TaskStatus.DONE
        self.completed_at = datetime.now()
        self.result = result
    
    def fail(self, error_message: str):
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
        self.error_message = error_message
