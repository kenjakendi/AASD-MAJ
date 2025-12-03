from typing import Dict
from datetime import datetime
import uuid

from spade.template import Template

from agents.base_agent import BaseAgent
from models.animal import Animal
from models.enums import AnimalHealthStatus, AnimalAdoptionStatus
from behaviours.reception.register_animal_behaviour import RegisterAnimalBehaviour
from behaviours.reception.receive_checkup_confirmation_behaviour import ReceiveCheckupConfirmationBehaviour
from behaviours.reception.receive_registration_request_behaviour import ReceiveRegistrationRequestBehaviour
from config.settings import Settings

# Import for dynamic agent creation
import asyncio


class ReceptionAgent(BaseAgent):
    
    def __init__(self, jid: str, password: str, config: Dict):
        super().__init__(jid, password, config)
        self.coordinator_jid = Settings.get_coordinator_jid()
        self.operating_hours = config.get('operating_hours', {})
        self.quarantine_room_id = config.get('quarantine_room_id', 'R004')
        self.registered_animals = []
        self.active_animal_agents = {}  # Map animal_id -> AnimalAssistantAgent
    
    async def setup(self):
        await super().setup()
        
        self.logger.info("Setting up Reception Agent")
        
        # Behaviour 1: Register Animal (Periodic - simulates intake)
        self.add_behaviour(RegisterAnimalBehaviour(period=120))  # Check every 2 minutes
        
        # Behaviour 2: Receive Initial Checkup Confirmations
        checkup_template = Template()
        checkup_template.set_metadata("protocol", "InitialCheckupComplete")
        self.add_behaviour(ReceiveCheckupConfirmationBehaviour(), checkup_template)

        # Behaviour 3: Receive External Registration Requests
        registration_template = Template()
        registration_template.set_metadata("protocol", "RegisterAnimalRequest")
        self.add_behaviour(ReceiveRegistrationRequestBehaviour(), registration_template)

        self.logger.info("Reception Agent is ready")
    
    async def register_new_animal(self, animal_data: Dict) -> str:
        # Generate animal ID
        animal_id = animal_data.get('id', f"A{str(uuid.uuid4())[:8].upper()}")
        
        # Create animal record
        animal = Animal(
            animal_id=animal_id,
            name=animal_data['name'],
            species=animal_data['species'],
            breed=animal_data.get('breed', 'Unknown'),
            age=animal_data.get('age', 0),
            sex=animal_data.get('sex', 'unknown'),
            health_status=AnimalHealthStatus.NEEDS_CHECKUP,
            dietary_requirements=animal_data.get('dietary_requirements', 'standard'),
            behavioral_notes=animal_data.get('behavioral_notes', ''),
            adoption_status=AnimalAdoptionStatus.NOT_AVAILABLE,  # Until initial checkup
            intake_date=datetime.now()
        )
        
        self.registered_animals.append(animal)
        
        self.logger.info(f"Registered new animal: {animal.name} (ID: {animal_id})")
        
        # Notify coordinator
        registration_data = {
            'animalId': animal_id,
            'name': animal.name,
            'species': animal.species,
            'breed': animal.breed,
            'age': animal.age,
            'sex': animal.sex,
            'dietaryRequirements': animal.dietary_requirements,
            'behavioralNotes': animal.behavioral_notes,
            'intakeDate': animal.intake_date.isoformat(),
            'quarantineRoomId': self.quarantine_room_id
        }
        
        await self.send_request(
            to=self.coordinator_jid,
            protocol='RegisterNewAnimal',
            content=registration_data
        )
        
        return animal_id
    
    async def create_animal_agent(self, animal: Animal) -> bool:
        try:
            # Import here to avoid circular imports
            from agents.animal_assistant_agent import AnimalAssistantAgent

            # Create JID for the new animal agent
            jid = f"animal_{animal.animal_id}@{Settings.XMPP_SERVER}"
            password = Settings.AGENT_PASSWORD

            # Prepare animal data
            animal_data = animal.to_dict()

            self.logger.info(f"Creating Animal Assistant Agent for {animal.name} ({animal.animal_id})")

            # Create and start the agent
            agent = AnimalAssistantAgent(jid, password, animal_data)
            await agent.start_with_retry(max_retries=Settings.MAX_RETRIES, delay=Settings.RETRY_DELAY)

            # Store reference to the agent
            self.active_animal_agents[animal.animal_id] = agent

            self.logger.info(f"✅ Animal Assistant Agent created successfully for {animal.name}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to create Animal Assistant Agent for {animal.animal_id}: {e}")
            return False

    def is_open(self) -> bool:
        now = datetime.now()
        day_name = now.strftime('%A').lower()

        if day_name not in self.operating_hours:
            return False

        # Check if within operating hours
        # Simplified check - in real system would parse time ranges
        return len(self.operating_hours[day_name]) > 0
