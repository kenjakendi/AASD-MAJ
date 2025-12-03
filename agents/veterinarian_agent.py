from typing import Dict
import asyncio

from spade.template import Template

from agents.worker_agent import WorkerAgent
from models.task import Task, TaskType
from behaviours.worker.receive_task_behaviour import ReceiveTaskBehaviour
from behaviours.worker.execute_task_behaviour import ExecuteTaskBehaviour
from behaviours.worker.update_availability_behaviour import UpdateAvailabilityBehaviour
from config.settings import Settings


class VeterinarianAgent(WorkerAgent):
    
    def __init__(self, jid: str, password: str, config: Dict):
        super().__init__(jid, password, config)
        self.specializations = set(config.get('specializations', []))
        self.emergency_available = config.get('emergency_available', False)
    
    async def setup(self):
        await super().setup()
        
        self.logger.info(f"Setting up Veterinarian Agent: {self.worker_name}")
        
        # Behaviour 1: Receive Vaccination Tasks
        vacc_template = Template()
        vacc_template.set_metadata("protocol", "AssignVaccinationTask")
        self.add_behaviour(ReceiveTaskBehaviour(), vacc_template)
        
        # Behaviour 2: Receive Health Check Tasks
        health_template = Template()
        health_template.set_metadata("protocol", "HealthRequestTask")
        self.add_behaviour(ReceiveTaskBehaviour(), health_template)
        
        # Behaviour 3: Receive Initial Checkup Tasks
        checkup_template = Template()
        checkup_template.set_metadata("protocol", "AssignInitialCheckupTask")
        self.add_behaviour(ReceiveTaskBehaviour(), checkup_template)
        
        # Behaviour 4: Execute Tasks
        self.add_behaviour(ExecuteTaskBehaviour(period=2))
        
        # Behaviour 5: Update Availability
        update_interval = Settings.WORKER_AVAILABILITY_UPDATE_INTERVAL
        self.add_behaviour(UpdateAvailabilityBehaviour(period=update_interval))
        
        self.logger.info(f"Veterinarian {self.worker_name} is ready")
    
    async def execute_task(self, task: Task) -> Dict:
        self.logger.info(f"Veterinarian {self.worker_id} executing {task.task_type.value} task {task.task_id}")
        
        start_time = asyncio.get_event_loop().time()
        
        if task.task_type == TaskType.VACCINATION:
            result = await self._execute_vaccination_task(task)
        elif task.task_type == TaskType.HEALTH_CHECK:
            result = await self._execute_health_check_task(task)
        elif task.task_type == TaskType.INITIAL_CHECKUP:
            result = await self._execute_initial_checkup_task(task)
        else:
            self.logger.error(f"Unknown task type: {task.task_type}")
            return {'success': False, 'error': 'Unknown task type'}
        
        end_time = asyncio.get_event_loop().time()
        execution_time = end_time - start_time
        self.total_work_time += execution_time
        
        result['execution_time'] = execution_time
        return result
    
    async def _execute_vaccination_task(self, task: Task) -> Dict:
        animal_id = task.parameters.get('animalId')
        vaccination_type = task.parameters.get('vaccinationType', 'routine')
        
        self.logger.info(f"Vaccinating animal {animal_id} ({vaccination_type})")
        
        await asyncio.sleep(Settings.VACCINATION_TASK_DURATION)
        
        self.logger.info(f"Animal {animal_id} has been vaccinated")
        
        return {
            'success': True,
            'animalId': animal_id,
            'vaccinationType': vaccination_type,
            'vaccinated': True,
            'worker': self.worker_id,
            'timestamp': asyncio.get_event_loop().time()
        }
    
    async def _execute_health_check_task(self, task: Task) -> Dict:
        animal_id = task.parameters.get('animalId')
        
        self.logger.info(f"Performing health check for animal {animal_id}")
        
        await asyncio.sleep(Settings.HEALTH_CHECK_DURATION)
        
        # Simulate health check result
        health_status = 'healthy'  # In real system, would be determined by examination
        
        self.logger.info(f"Health check complete for animal {animal_id}: {health_status}")
        
        return {
            'success': True,
            'animalId': animal_id,
            'healthStatus': health_status,
            'newState': 'healthy',
            'worker': self.worker_id,
            'timestamp': asyncio.get_event_loop().time()
        }
    
    async def _execute_initial_checkup_task(self, task: Task) -> Dict:
        animal_id = task.parameters.get('animalId')
        
        self.logger.info(f"Performing initial checkup for new animal {animal_id}")
        
        await asyncio.sleep(Settings.INITIAL_CHECKUP_DURATION)
        
        # Comprehensive initial examination
        health_status = 'healthy'
        vaccinations_needed = task.parameters.get('vaccinationsNeeded', [])
        
        self.logger.info(f"Initial checkup complete for animal {animal_id}")
        
        return {
            'success': True,
            'animalId': animal_id,
            'healthStatus': health_status,
            'newState': 'healthy',
            'vaccinationsNeeded': vaccinations_needed,
            'clearForAdoption': health_status == 'healthy',
            'worker': self.worker_id,
            'timestamp': asyncio.get_event_loop().time()
        }
