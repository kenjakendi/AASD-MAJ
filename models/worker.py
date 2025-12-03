from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from models.enums import WorkerRole


@dataclass
class WorkerAvailability:
    worker_id: str
    schedule: Dict[str, List[str]] = field(default_factory=dict)  # day -> ["HH:MM-HH:MM", ...]
    is_available: bool = True
    current_load: int = 0
    max_concurrent_tasks: int = 2
    
    def to_dict(self) -> Dict:
        return {
            'worker_id': self.worker_id,
            'schedule': self.schedule,
            'is_available': self.is_available,
            'current_load': self.current_load,
            'max_concurrent_tasks': self.max_concurrent_tasks
        }


@dataclass
class Worker:
    worker_id: str
    name: str
    role: WorkerRole
    competencies: Set[str] = field(default_factory=set)
    max_concurrent_tasks: int = 2
    
    # Availability
    availability: WorkerAvailability = None
    
    # Preferences
    preferences: Dict = field(default_factory=dict)
    
    # Statistics
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_work_hours: float = 0.0
    
    def __post_init__(self):
        if self.availability is None:
            self.availability = WorkerAvailability(
                worker_id=self.worker_id,
                max_concurrent_tasks=self.max_concurrent_tasks
            )
    
    def to_dict(self) -> Dict:
        return {
            'worker_id': self.worker_id,
            'name': self.name,
            'role': self.role.value,
            'competencies': list(self.competencies),
            'max_concurrent_tasks': self.max_concurrent_tasks,
            'availability': self.availability.to_dict() if self.availability else None,
            'preferences': self.preferences,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'total_work_hours': self.total_work_hours
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Worker':
        worker = cls(
            worker_id=data['worker_id'],
            name=data['name'],
            role=WorkerRole(data['role']),
            competencies=set(data.get('competencies', [])),
            max_concurrent_tasks=data.get('max_concurrent_tasks', 2),
            preferences=data.get('preferences', {}),
            tasks_completed=data.get('tasks_completed', 0),
            tasks_failed=data.get('tasks_failed', 0),
            total_work_hours=data.get('total_work_hours', 0.0)
        )
        
        if data.get('availability'):
            avail_data = data['availability']
            worker.availability = WorkerAvailability(
                worker_id=avail_data['worker_id'],
                schedule=avail_data.get('schedule', {}),
                is_available=avail_data.get('is_available', True),
                current_load=avail_data.get('current_load', 0),
                max_concurrent_tasks=avail_data.get('max_concurrent_tasks', 2)
            )
        
        return worker
    
    def can_handle_task(self, task_type: str) -> bool:
        return task_type in self.competencies
    
    def is_available_for_task(self) -> bool:
        if not self.availability:
            return False
        return (self.availability.is_available and 
                self.availability.current_load < self.max_concurrent_tasks)
    
    def assign_task(self):
        if self.availability:
            self.availability.current_load += 1
            self.availability.is_available = (
                self.availability.current_load < self.max_concurrent_tasks
            )
    
    def complete_task(self, success: bool = True):
        if self.availability:
            self.availability.current_load = max(0, self.availability.current_load - 1)
            self.availability.is_available = (
                self.availability.current_load < self.max_concurrent_tasks
            )
        
        if success:
            self.tasks_completed += 1
        else:
            self.tasks_failed += 1
