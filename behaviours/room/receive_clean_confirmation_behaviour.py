import json
from spade.behaviour import CyclicBehaviour


class ReceiveCleanConfirmationBehaviour(CyclicBehaviour):
    
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            try:
                content = json.loads(msg.body)
                
                self.agent.logger.info(f"Received cleaning confirmation")
                
                # Update room state
                if content.get('success'):
                    self.agent.mark_clean()
                    
            except Exception as e:
                self.agent.logger.error(f"Error processing clean confirmation: {e}")
