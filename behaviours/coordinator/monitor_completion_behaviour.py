import json
from spade.behaviour import CyclicBehaviour


class MonitorCompletionBehaviour(CyclicBehaviour):
    
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            try:
                content = json.loads(msg.body)
                protocol = msg.get_metadata("protocol")
                
                self.agent.logger.info(f"Received completion: {protocol}")
                
                task_id = content.get('taskId')
                if task_id and task_id in self.agent.active_tasks:
                    result = content

                    # Notify relevant entities BEFORE marking complete (while task still in active_tasks)
                    await self._notify_completion(content, protocol)

                    # Now mark task as complete
                    self.agent.mark_task_complete(task_id, result)
                    
            except Exception as e:
                self.agent.logger.error(f"Error processing completion: {e}")
    
    async def _notify_completion(self, content: dict, protocol: str):
        from models.task import TaskType
        
        animal_id = content.get('animalId')
        room_id = content.get('roomId')
        task_id = content.get('taskId')
        
        # Special handling for INITIAL_CHECKUP completion
        if task_id and task_id in self.agent.active_tasks:
            task = self.agent.active_tasks[task_id]
            if task.task_type == TaskType.INITIAL_CHECKUP and content.get('success'):
                await self._handle_initial_checkup_completion(task, content)
        
        # Notify animal assistant if relevant
        if animal_id:
            animal_jid = f"animal_{animal_id}@{self.agent.config.get('domain', 'serverhello')}"
            await self.agent.send_confirm(to=animal_jid, protocol=protocol, content=content)
        
        # Notify room agent if relevant
        if room_id:
            room_jid = f"room_{room_id}@{self.agent.config.get('domain', 'serverhello')}"
            await self.agent.send_confirm(to=room_jid, protocol=protocol, content=content)
    
    async def _handle_initial_checkup_completion(self, task, completion_data):
        animal_id = task.parameters.get('animalId') or completion_data.get('animalId')
        if not animal_id:
            return
        
        self.agent.logger.info(f"Processing initial checkup completion for animal {animal_id}")
        
        # Extract checkup results
        health_status = completion_data.get('healthStatus', 'unknown')
        vaccinations_needed = completion_data.get('vaccinationsNeeded', [])
        clear_for_adoption = completion_data.get('clearForAdoption', False)
        
        # 1. Notify reception about checkup completion
        from config.settings import Settings
        from models.enums import Priority
        reception_jid = Settings.get_reception_jid()
        
        await self.agent.send_inform(
            to=reception_jid,
            protocol='InitialCheckupComplete',
            content={
                'animalId': animal_id,
                'healthStatus': health_status,
                'vaccinationsNeeded': vaccinations_needed,
                'clearForAdoption': clear_for_adoption,
                'registrationComplete': True
            }
        )
        
        self.agent.logger.info(f"Notified reception about completed checkup for animal {animal_id}")
        
        # 2. Schedule vaccinations if needed
        if vaccinations_needed:
            for vaccination_type in vaccinations_needed:
                self.agent.add_request(
                    'vaccination',
                    {
                        'animalId': animal_id,
                        'vaccinationType': vaccination_type
                    },
                    Priority.HIGH
                )
            
            self.agent.logger.info(f"Scheduled {len(vaccinations_needed)} vaccinations for animal {animal_id}")
        
        # 3. If animal is clear for adoption, update status
        if clear_for_adoption:
            self.agent.logger.info(f"Animal {animal_id} is clear for adoption and ready for monitoring")
