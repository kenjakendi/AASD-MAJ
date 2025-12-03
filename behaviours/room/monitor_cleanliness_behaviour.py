from spade.behaviour import PeriodicBehaviour


class MonitorCleanlinessBehaviour(PeriodicBehaviour):
    
    async def run(self):
        
        # Ensure agent is alive before sending messages
        if not self.agent.is_alive():
            return
        
        # Check if scheduled for cleaning
        if self.agent.is_scheduled_for_cleaning():
            if self.agent.needs_cleaning():
                await self.agent.request_cleaning()
        
        # Check if needs cleaning regardless of schedule
        elif self.agent.needs_cleaning():
            await self.agent.request_cleaning()
