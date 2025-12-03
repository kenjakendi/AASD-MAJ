from typing import Dict, List, Set, Optional
from datetime import datetime, timedelta
import asyncio

from spade.template import Template

from agents.base_agent import BaseAgent
from models.task import Task, TaskStatus, TaskType
from models.enums import Priority
from behaviours.coordinator.receive_requests_behaviour import (
    ReceiveCleanRequestBehaviour,
    ReceiveFeedRequestBehaviour,
    ReceiveWalkRequestBehaviour,
    ReceiveHealthRequestBehaviour,
    ReceiveVaccinationRequestBehaviour,
    ReceiveNewAnimalBehaviour,
    ReceiveAdoptionApplicationBehaviour
)
from behaviours.coordinator.assign_tasks_behaviour import AssignTasksBehaviour
from behaviours.coordinator.monitor_completion_behaviour import MonitorCompletionBehaviour
from behaviours.coordinator.priority_management_behaviour import PriorityManagementBehaviour
from behaviours.coordinator.worker_availability_behaviour import WorkerAvailabilityBehaviour
from utils.task_generator import TaskGenerator
from utils.scheduler import VaccinationScheduler


class CoordinatorAgent(BaseAgent):
    
    def __init__(self, jid: str, password: str, config: Dict):
        super().__init__(jid, password, config)
        
        # Task management
        self.pending_requests: List[Dict] = []
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: List[Task] = []
        self.failed_tasks: List[Task] = []
        
        # Worker management
        self.worker_availability: Dict[str, bool] = {}
        self.worker_competencies: Dict[str, Set[str]] = {}
        self.worker_current_load: Dict[str, int] = {}
        self.worker_max_concurrent_tasks: Dict[str, int] = {}
        self.worker_jids: Dict[str, str] = {}  # Map worker_id to actual JID
        self.worker_preferences: Dict[str, Dict] = {}
        
        # Animal and room tracking
        self.animal_task_history: Dict[str, List[str]] = {}
        self.room_last_cleaned: Dict[str, datetime] = {}
        
        # Assignment strategy
        self.assignment_strategy = config.get('assignment_strategy', 'round_robin')
        self.last_assigned_worker: Dict[TaskType, str] = {}
        
        # Task generator and scheduler
        self.task_generator = TaskGenerator()
        self.vaccination_scheduler = VaccinationScheduler()
        
        # Statistics
        self.stats = {
            'total_tasks_assigned': 0,
            'total_tasks_completed': 0,
            'total_tasks_failed': 0,
            'emergency_tasks_handled': 0
        }
    
    async def setup(self):
        await super().setup()
        
        self.logger.info("Setting up Coordinator Agent")
        
        # Behaviour 1: Receive Clean Requests
        clean_template = Template()
        clean_template.set_metadata("protocol", "CleanRequest")
        self.add_behaviour(ReceiveCleanRequestBehaviour(), clean_template)
        
        # Behaviour 2: Receive Feed Requests
        feed_template = Template()
        feed_template.set_metadata("protocol", "FeedRequest")
        self.add_behaviour(ReceiveFeedRequestBehaviour(), feed_template)
        
        # Behaviour 3: Receive Walk Requests
        walk_template = Template()
        walk_template.set_metadata("protocol", "WalkRequest")
        self.add_behaviour(ReceiveWalkRequestBehaviour(), walk_template)
        
        # Behaviour 4: Receive Health Requests
        health_template = Template()
        health_template.set_metadata("protocol", "HealthRequest")
        self.add_behaviour(ReceiveHealthRequestBehaviour(), health_template)

        # Behaviour 5: Receive Vaccination Requests
        vaccination_template = Template()
        vaccination_template.set_metadata("protocol", "VaccinationRequest")
        self.add_behaviour(ReceiveVaccinationRequestBehaviour(), vaccination_template)

        # Behaviour 6: Receive New Animal Registrations
        registration_template = Template()
        registration_template.set_metadata("protocol", "RegisterNewAnimal")
        self.add_behaviour(ReceiveNewAnimalBehaviour(), registration_template)

        # Behaviour 7: Receive Adoption Applications
        adoption_template = Template()
        adoption_template.set_metadata("protocol", "AdoptionApplicationRequest")
        self.add_behaviour(ReceiveAdoptionApplicationBehaviour(), adoption_template)

        # Behaviour 8: Monitor Worker Availability
        availability_template = Template()
        availability_template.set_metadata("protocol", "UpdateWorkerAvailability")
        self.add_behaviour(WorkerAvailabilityBehaviour(), availability_template)

        # Behaviour 9: Assign Tasks (Periodic)
        task_check_interval = self.config.get('task_check_interval', 5)
        self.add_behaviour(AssignTasksBehaviour(period=task_check_interval))

        # Behaviour 10: Monitor Task Completion
        completion_template = Template()
        completion_template.set_metadata("performative", "confirm")
        self.add_behaviour(MonitorCompletionBehaviour(), completion_template)

        # Behaviour 11: Priority Management (Periodic)
        if self.config.get('enable_priority_management', True):
            self.add_behaviour(PriorityManagementBehaviour(period=10))
        
        self.logger.info("Coordinator Agent setup complete")
    
    def add_request(self, request_type: str, request_data: Dict, priority: Priority = Priority.NORMAL):
        request = {
            'type': request_type,
            'data': request_data,
            'priority': priority,
            'timestamp': datetime.now(),
            'attempts': 0
        }
        self.pending_requests.append(request)
        self.logger.info(f"Added {request_type} request: {request_data}")
    
    def get_available_workers(self, task_type: TaskType) -> List[str]:
        available = []
        self.logger.info(f"Checking worker availability for task type: {task_type.value}")
        for worker_id in self.worker_competencies.keys():
            # Check if worker has the required competency
            if task_type.value not in self.worker_competencies.get(worker_id, set()):
                continue

            # With queue system, workers accept tasks even at capacity
            # Add to list regardless of current load
            current_load = self.worker_current_load.get(worker_id, 0)
            max_tasks = self.worker_max_concurrent_tasks.get(worker_id, 1)
            available.append(worker_id)
            self.logger.debug(f"Worker {worker_id} available for queueing: load={current_load}/{max_tasks}")

        self.logger.info(f"Available workers for {task_type.value}: {available}")
        return available
    
    def select_worker(self, task_type: TaskType, available_workers: List[str]) -> Optional[str]:
        if not available_workers:
            return None
        
        if self.assignment_strategy == 'round_robin':
            # Simple round-robin
            last_worker = self.last_assigned_worker.get(task_type)
            if last_worker in available_workers:
                idx = available_workers.index(last_worker)
                next_idx = (idx + 1) % len(available_workers)
                return available_workers[next_idx]
            return available_workers[0]
        
        elif self.assignment_strategy == 'least_loaded':
            # Assign to worker with least current load
            return min(available_workers, 
                      key=lambda w: self.worker_current_load.get(w, 0))
        
        elif self.assignment_strategy == 'priority':
            # Consider worker preferences
            # TODO: Implement preference-based selection
            return available_workers[0]
        
        return available_workers[0]
    
    def generate_task_id(self) -> str:
        timestamp = datetime.now().timestamp()
        count = len(self.active_tasks) + len(self.completed_tasks)
        return f"task_{int(timestamp)}_{count}"
    
    def mark_task_complete(self, task_id: str, result: Dict):
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = TaskStatus.DONE
            task.completed_at = datetime.now()
            task.result = result

            self.completed_tasks.append(task)
            del self.active_tasks[task_id]

            # Worker will report their own updated availability and load
            # No need to manually update it here

            self.stats['total_tasks_completed'] += 1
            self.logger.info(f"Task {task_id} completed successfully")
    
    def get_statistics(self) -> Dict:
        return {
            **self.stats,
            'pending_requests': len(self.pending_requests),
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.completed_tasks),
            'failed_tasks': len(self.failed_tasks),
            'available_workers': sum(1 for av in self.worker_availability.values() if av)
        }
