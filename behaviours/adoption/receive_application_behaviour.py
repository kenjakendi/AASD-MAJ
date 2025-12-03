import json
from spade.behaviour import CyclicBehaviour


class ReceiveApplicationBehaviour(CyclicBehaviour):
    
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            try:
                content = json.loads(msg.body)
                
                self.agent.logger.info(f"Received adoption application task")
                
                # Receive and process application
                application_id = await self.agent.receive_application(content)
                
            except Exception as e:
                self.agent.logger.error(f"Error receiving application: {e}")
