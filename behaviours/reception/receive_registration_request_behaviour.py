import json
from spade.behaviour import CyclicBehaviour


class ReceiveRegistrationRequestBehaviour(CyclicBehaviour):

    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            try:
                content = json.loads(msg.body)

                self.agent.logger.info(f"Received external registration request: {content}")

                # Extract animal data
                animal_data = {
                    'name': content.get('name'),
                    'species': content.get('species'),
                    'breed': content.get('breed', 'Unknown'),
                    'age': content.get('age', 0),
                    'sex': content.get('sex', 'unknown'),
                    'dietary_requirements': content.get('dietary_requirements', 'standard'),
                    'behavioral_notes': content.get('behavioral_notes', ''),
                }

                # Register the animal
                animal_id = await self.agent.register_new_animal(animal_data)

                # Send confirmation back to sender
                sender_jid = str(msg.sender)
                await self.agent.send_confirm(
                    to=sender_jid,
                    protocol='RegistrationConfirmation',
                    content={
                        'animalId': animal_id,
                        'name': animal_data['name'],
                        'success': True,
                        'message': f'Animal {animal_data["name"]} registered successfully with ID {animal_id}'
                    }
                )

                self.agent.logger.info(f"✅ Registered animal {animal_data['name']} with ID {animal_id}")

            except Exception as e:
                self.agent.logger.error(f"Error processing registration request: {e}")
