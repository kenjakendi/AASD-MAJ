from typing import Dict, List, Optional, Set
from datetime import datetime, time as dt_time
from abc import ABC, abstractmethod

from agents.base_agent import BaseAgent
from models.task import Task, TaskStatus
from models.enums import WorkerRole


class WorkerAgent(BaseAgent, ABC):
    
    def __init__(self, jid: str, password: str, config: Dict):
        super().__init__(jid, password, config)
        
        # Worker identity
        self.worker_id = config['worker_id']
        self.worker_name = config.get('name', self.worker_id)
        self.role = WorkerRole(config['role'])
        
        # Competencies and limits
        self.competencies: Set[str] = set(config.get('competencies', []))
        self.max_concurrent_tasks = config.get('max_concurrent_tasks', 2)
        
        # Availability
        self.availability_schedule = config.get('availability', {})
        self.is_available = True
        self.task_queue: List[Task] = []  # Queue of tasks to execute
        self.current_tasks: List[Task] = []  # Currently executing tasks
        
        # Preferences
        self.preferences = config.get('preferences', {})
        
        # Statistics
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.total_work_time = 0.0
    
    def is_currently_available(self) -> bool:
        # Check time-based availability
        now = datetime.now()
        day_name = now.strftime('%A').lower()
        
        if day_name not in self.availability_schedule:
            return False
        
        time_slots = self.availability_schedule[day_name]
        if not time_slots:
            return False
        
        current_time = now.time()
        for slot in time_slots:
            start_str, end_str = slot.split('-')
            start_time = dt_time.fromisoformat(start_str)
            end_time = dt_time.fromisoformat(end_str)
            
            if start_time <= current_time <= end_time:
                # Within working hours, check load
                return len(self.current_tasks) < self.max_concurrent_tasks
        
        return False
    
    def can_handle_task(self, task_type: str) -> bool:
        return task_type in self.competencies
    
    def add_task(self, task: Task):
        self.task_queue.append(task)
        self.logger.info(f"Task {task.task_id} added to queue (queue size: {len(self.task_queue)})")
        return True
    
    def complete_task(self, task_id: str):
        self.current_tasks = [t for t in self.current_tasks if t.task_id != task_id]
        self.is_available = len(self.current_tasks) < self.max_concurrent_tasks
        self.tasks_completed += 1
    
    def get_current_load(self) -> int:
        return len(self.current_tasks)
    
    @abstractmethod
    async def execute_task(self, task: Task) -> Dict:
        pass
    
    def get_statistics(self) -> Dict:
        return {
            'worker_id': self.worker_id,
            'role': self.role.value,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'current_load': self.get_current_load(),
            'is_available': self.is_available,
            'total_work_time': self.total_work_time
        }
