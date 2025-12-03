from typing import Dict
import asyncio

from spade.template import Template

from agents.worker_agent import WorkerAgent
from models.task import Task, TaskType
from behaviours.worker.receive_task_behaviour import ReceiveTaskBehaviour
from behaviours.worker.execute_task_behaviour import ExecuteTaskBehaviour
from behaviours.worker.update_availability_behaviour import UpdateAvailabilityBehaviour
from config.settings import Settings


class CaretakerAgent(WorkerAgent):
    
    async def setup(self):
        await super().setup()
        
        self.logger.info(f"Setting up Caretaker Agent: {self.worker_name}")
        
        # Behaviour 1: Receive Feed Tasks
        feed_template = Template()
        feed_template.set_metadata("protocol", "AssignFeedTask")
        self.add_behaviour(ReceiveTaskBehaviour(), feed_template)
        
        # Behaviour 2: Receive Walk Tasks
        walk_template = Template()
        walk_template.set_metadata("protocol", "AssignWalkTask")
        self.add_behaviour(ReceiveTaskBehaviour(), walk_template)
        
        # Behaviour 3: Execute Tasks
        self.add_behaviour(ExecuteTaskBehaviour(period=2))
        
        # Behaviour 4: Update Availability
        update_interval = Settings.WORKER_AVAILABILITY_UPDATE_INTERVAL
        self.add_behaviour(UpdateAvailabilityBehaviour(period=update_interval))
        
        self.logger.info(f"Caretaker {self.worker_name} is ready")
    
    async def execute_task(self, task: Task) -> Dict:
        self.logger.info(f"Caretaker {self.worker_id} executing {task.task_type.value} task {task.task_id}")
        
        start_time = asyncio.get_event_loop().time()
        
        if task.task_type == TaskType.FEED:
            result = await self._execute_feed_task(task)
        elif task.task_type == TaskType.WALK:
            result = await self._execute_walk_task(task)
        else:
            self.logger.error(f"Unknown task type: {task.task_type}")
            return {'success': False, 'error': 'Unknown task type'}
        
        end_time = asyncio.get_event_loop().time()
        execution_time = end_time - start_time
        self.total_work_time += execution_time
        
        result['execution_time'] = execution_time
        return result
    
    async def _execute_feed_task(self, task: Task) -> Dict:
        animal_id = task.parameters.get('animalId')
        
        self.logger.info(f"Feeding animal {animal_id}")
        
        # Simulate feeding
        await asyncio.sleep(Settings.FEED_TASK_DURATION)
        
        self.logger.info(f"Animal {animal_id} has been fed")
        
        return {
            'success': True,
            'animalId': animal_id,
            'newState': 'fed',
            'worker': self.worker_id,
            'timestamp': asyncio.get_event_loop().time()
        }
    
    async def _execute_walk_task(self, task: Task) -> Dict:
        animal_id = task.parameters.get('animalId')
        
        self.logger.info(f"Walking animal {animal_id}")
        
        # Simulate walking
        await asyncio.sleep(Settings.WALK_TASK_DURATION)
        
        self.logger.info(f"Animal {animal_id} has been walked")
        
        return {
            'success': True,
            'animalId': animal_id,
            'newState': 'walked',
            'worker': self.worker_id,
            'timestamp': asyncio.get_event_loop().time()
        }
