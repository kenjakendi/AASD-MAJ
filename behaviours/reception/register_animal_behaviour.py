from spade.behaviour import PeriodicBehaviour
import random


class RegisterAnimalBehaviour(PeriodicBehaviour):
    
    async def run(self):
        
        # Only register during operating hours
        if not self.agent.is_open():
            return
        
        # Randomly decide if a new animal arrives (10% chance per check)
        if random.random() < 0.1:
            # Simulate new animal data
            animal_data = self._generate_sample_animal()
            
            await self.agent.register_new_animal(animal_data)
    
    def _generate_sample_animal(self) -> dict:
        import uuid
        
        species_options = ['dog', 'cat']
        breed_options = {
            'dog': ['Mixed', 'Labrador', 'German Shepherd', 'Golden Retriever'],
            'cat': ['Mixed', 'Persian', 'Siamese', 'Maine Coon']
        }
        
        species = random.choice(species_options)
        breed = random.choice(breed_options[species])
        
        names = ['Max', 'Bella', 'Charlie', 'Luna', 'Rocky', 'Mia', 'Buddy', 'Daisy']
        
        return {
            'name': random.choice(names),
            'species': species,
            'breed': breed,
            'age': random.randint(1, 10),
            'sex': random.choice(['male', 'female']),
            'dietary_requirements': random.choice(['standard', 'sensitive_stomach', 'special_diet']),
            'behavioral_notes': 'Friendly and playful'
        }
