from spade.behaviour import PeriodicBehaviour
from config.settings import Settings


class UpdateAvailabilityBehaviour(PeriodicBehaviour):
    
    async def run(self):
        
        # Ensure agent is alive before sending messages
        if not self.agent.is_alive():
            return
            
        coordinator_jid = Settings.get_coordinator_jid()
        
        # Check current availability
        is_available = self.agent.is_currently_available()
        current_load = self.agent.get_current_load()
        
        content = {
            'workerId': self.agent.worker_id,
            'workerJid': str(self.agent.jid),  # Send actual JID for proper routing
            'isAvailable': is_available,
            'currentLoad': current_load,
            'maxConcurrentTasks': self.agent.max_concurrent_tasks,
            'competencies': list(self.agent.competencies)
        }
        
        await self.agent.send_request(
            to=coordinator_jid,
            protocol='UpdateWorkerAvailability',
            content=content
        )
        
        self.agent.logger.info(f"Sent availability update: available={is_available}, load={current_load}")
