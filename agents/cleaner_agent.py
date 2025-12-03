from typing import Dict
import asyncio

from spade.template import Template

from agents.worker_agent import WorkerAgent
from models.task import Task, TaskType
from behaviours.worker.receive_task_behaviour import ReceiveTaskBehaviour
from behaviours.worker.execute_task_behaviour import ExecuteTaskBehaviour
from behaviours.worker.update_availability_behaviour import UpdateAvailabilityBehaviour
from config.settings import Settings


class CleanerAgent(WorkerAgent):
    
    async def setup(self):
        await super().setup()
        
        self.logger.info(f"Setting up Cleaner Agent: {self.worker_name}")
        
        # Behaviour 1: Receive Clean Tasks
        clean_template = Template()
        clean_template.set_metadata("protocol", "AssignCleanTask")
        self.add_behaviour(ReceiveTaskBehaviour(), clean_template)
        
        # Behaviour 2: Execute Tasks
        self.add_behaviour(ExecuteTaskBehaviour(period=2))
        
        # Behaviour 3: Update Availability
        update_interval = Settings.WORKER_AVAILABILITY_UPDATE_INTERVAL
        self.add_behaviour(UpdateAvailabilityBehaviour(period=update_interval))
        
        self.logger.info(f"Cleaner {self.worker_name} is ready")
    
    async def execute_task(self, task: Task) -> Dict:
        self.logger.info(f"Cleaner {self.worker_id} executing clean task {task.task_id}")
        
        start_time = asyncio.get_event_loop().time()
        
        result = await self._execute_clean_task(task)
        
        end_time = asyncio.get_event_loop().time()
        execution_time = end_time - start_time
        self.total_work_time += execution_time
        
        result['execution_time'] = execution_time
        return result
    
    async def _execute_clean_task(self, task: Task) -> Dict:
        room_id = task.parameters.get('roomId')
        special_cleaning = task.parameters.get('requiresSpecialCleaning', False)
        
        self.logger.info(f"Cleaning room {room_id}" + 
                        (" (special cleaning)" if special_cleaning else ""))
        
        # Simulate cleaning (longer for special cleaning)
        duration = Settings.CLEAN_TASK_DURATION
        if special_cleaning:
            duration *= 1.5
        
        await asyncio.sleep(duration)
        
        self.logger.info(f"Room {room_id} has been cleaned")
        
        return {
            'success': True,
            'roomId': room_id,
            'newState': 'clean',
            'specialCleaning': special_cleaning,
            'worker': self.worker_id,
            'timestamp': asyncio.get_event_loop().time()
        }
