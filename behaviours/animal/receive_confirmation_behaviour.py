import json
from spade.behaviour import CyclicBehaviour


class ReceiveConfirmationBehaviour(CyclicBehaviour):
    
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            try:
                content = json.loads(msg.body)
                protocol = msg.get_metadata("protocol")
                
                self.agent.logger.info(f"Received confirmation: {protocol}")
                
                # Update animal state based on confirmation
                # Match exact protocol names for clarity and reliability
                if protocol == 'ConfirmFeedTask':
                    self.agent.update_feed_state()
                elif protocol == 'ConfirmWalkTask':
                    self.agent.update_walk_state()
                elif protocol == 'ConfirmHealthRequestTask':
                    new_state = content.get('newState', 'healthy')
                    self.agent.update_health_state(new_state)
                elif protocol == 'ConfirmVaccinationTask':
                    vaccination_type = content.get('vaccinationType', 'routine')
                    self.agent.update_vaccination_state(vaccination_type)
                elif protocol == 'ConfirmInitialCheckupTask':
                    self.agent.update_initial_checkup_state(content)
                elif protocol == 'ConfirmCleanTask':
                    # Room cleaning confirmation (if animal is in a room)
                    self.agent.logger.info(f"Room cleaning confirmed for {self.agent.animal.name}")
                else:
                    self.agent.logger.warning(f"Unknown confirmation protocol: {protocol}")
                    
            except Exception as e:
                self.agent.logger.error(f"Error processing confirmation: {e}")
