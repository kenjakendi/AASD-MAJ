from spade.behaviour import PeriodicBehaviour
import random


class SubmitApplicationBehaviour(PeriodicBehaviour):
    
    async def run(self):
        
        # Check if applicant has submission enabled
        submission_config = self.agent.config.get('submission_config', {})
        if not submission_config.get('enabled', False):
            return
        
        # Only submit if haven't submitted too many already
        if len(self.agent.submitted_applications) >= 3:
            self.agent.logger.debug(f"Applicant {self.agent.applicant_name} has already submitted 3 applications")
            return
        
        # Randomly decide if to submit (30% chance per check)
        if random.random() < .3:
            # Select a random animal ID to apply for
            # In real system, would query available animals
            # For simulation, use predefined IDs
            available_animals = ['001', '002', '003']
            preferred_species = submission_config.get('preferred_species', [])
            
            # Simple simulation: pick random animal
            animal_id = random.choice(available_animals)
            
            # Additional info for application
            additional_info = {
                'has_previous_pet_experience': random.choice([True, False]),
                'home_type': random.choice(['house', 'apartment']),
                'has_yard': random.choice([True, False]),
                'other_pets': random.choice([[], ['cat'], ['dog']]),
                'household_members': random.randint(1, 4),
                'employment_status': random.choice(['employed', 'self-employed', 'retired']),
                'references': [f'Reference {i}' for i in range(1, random.randint(2, 4))]
            }
            
            try:
                # Submit application
                application_id = await self.agent.submit_adoption_application(
                    animal_id=animal_id,
                    additional_info=additional_info
                )
                
                self.agent.logger.info(
                    f"Applicant {self.agent.applicant_name} submitted application {application_id} for animal {animal_id}"
                )
                
            except Exception as e:
                self.agent.logger.error(f"Error submitting application: {e}")







