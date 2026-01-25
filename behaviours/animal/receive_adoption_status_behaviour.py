import json
from spade.behaviour import CyclicBehaviour


class ReceiveAdoptionStatusBehaviour(CyclicBehaviour):
    
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            try:
                content = json.loads(msg.body)
                
                adoption_status = content.get('adoptionStatus')
                adopted_by = content.get('adoptedBy')
                adoption_date = content.get('adoptionDate')
                
                if adoption_status == 'adopted':
                    # Update animal's adoption status
                    from models.enums import AnimalAdoptionStatus
                    self.agent.animal.adoption_status = AnimalAdoptionStatus.ADOPTED

                    self.agent.logger.info(
                        f"🎉 {self.agent.animal.name} has been ADOPTED by {adopted_by}! "
                        f"No longer monitoring needs."
                    )

                    # Update the agent's config to reflect adoption status
                    self.agent.config['adoption_status'] = 'adopted'

                    # Update the dashboard tracker with new adoption status
                    await self.agent._update_tracker_metadata()

                    # Stop monitoring needs since animal is adopted
                    # The agent will continue to exist but won't request care
                    # Adoption status is now ADOPTED which will prevent care requests
                
            except Exception as e:
                self.agent.logger.error(f"Error processing adoption status update: {e}")






