import json
from spade.behaviour import CyclicBehaviour


class ReceiveCheckupConfirmationBehaviour(CyclicBehaviour):
    
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            try:
                content = json.loads(msg.body)
                
                animal_id = content.get('animalId')
                health_status = content.get('healthStatus')
                clear_for_adoption = content.get('clearForAdoption', False)
                
                self.agent.logger.info(
                    f"Received checkup confirmation for animal {animal_id}: "
                    f"health={health_status}, clear_for_adoption={clear_for_adoption}"
                )
                
                # Update registered animal record and create animal agent
                for animal in self.agent.registered_animals:
                    if animal.animal_id == animal_id:
                        # Update animal status
                        from models.enums import AnimalHealthStatus
                        animal.health_status = AnimalHealthStatus(health_status)
                        if clear_for_adoption:
                            from models.enums import AnimalAdoptionStatus
                            animal.adoption_status = AnimalAdoptionStatus.AVAILABLE

                        self.agent.logger.info(
                            f"Updated animal {animal_id} status: "
                            f"health={animal.health_status}, adoption={animal.adoption_status}"
                        )

                        # Create Animal Assistant Agent now that initial checkup is complete
                        if animal_id not in self.agent.active_animal_agents:
                            self.agent.logger.info(
                                f"Initial checkup complete for {animal_id}, creating Animal Assistant Agent..."
                            )
                            success = await self.agent.create_animal_agent(animal)
                            if success:
                                self.agent.logger.info(
                                    f"🎉 Animal {animal.name} ({animal_id}) is now active in the system!"
                                )
                            else:
                                self.agent.logger.error(
                                    f"Failed to activate Animal Assistant Agent for {animal_id}"
                                )
                        break
                
            except Exception as e:
                self.agent.logger.error(f"Error processing checkup confirmation: {e}")





