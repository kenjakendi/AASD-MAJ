from typing import Dict
from datetime import datetime

from spade.template import Template

from agents.base_agent import BaseAgent
from models.animal import Animal
from behaviours.animal.monitor_needs_behaviour import MonitorNeedsBehaviour
from behaviours.animal.receive_confirmation_behaviour import ReceiveConfirmationBehaviour
from behaviours.animal.receive_adoption_status_behaviour import ReceiveAdoptionStatusBehaviour
from config.settings import Settings


class AnimalAssistantAgent(BaseAgent):
    
    def __init__(self, jid: str, password: str, animal_data: Dict):
        super().__init__(jid, password, animal_data)
        self.animal = Animal.from_dict(animal_data)
        self.coordinator_jid = f"coordinator@{Settings.XMPP_SERVER}"

        # Track pending requests to avoid duplicates
        self.pending_feed_request = False
        self.pending_walk_request = False
        self.pending_health_request = False
        self.pending_vaccination_request = False
    
    async def setup(self):
        await super().setup()
        
        self.logger.info(f"Setting up Animal Assistant Agent for: {self.animal.name} ({self.animal.animal_id})")
        
        # Behaviour 1: Monitor Needs (Periodic)
        self.add_behaviour(MonitorNeedsBehaviour(period=Settings.TASK_CHECK_INTERVAL))
        
        # Behaviour 2: Receive Confirmations
        confirmation_template = Template()
        confirmation_template.set_metadata("performative", "confirm")
        self.add_behaviour(ReceiveConfirmationBehaviour(), confirmation_template)
        
        # Behaviour 3: Receive Adoption Status Updates
        adoption_template = Template()
        adoption_template.set_metadata("protocol", "UpdateAdoptionStatus")
        self.add_behaviour(ReceiveAdoptionStatusBehaviour(), adoption_template)
        
        self.logger.info(f"Animal Assistant for {self.animal.name} is ready")
    
    def needs_feeding(self) -> bool:
        return self.animal.needs_feeding(interval_hours=Settings.FEED_INTERVAL / 3600)
    
    def needs_walk(self) -> bool:
        return self.animal.needs_walk(interval_hours=Settings.WALK_INTERVAL / 3600)
    
    def needs_health_check(self) -> bool:
        return self.animal.needs_health_check()
    
    def needs_vaccination(self) -> bool:
        return self.animal.needs_vaccination()
    
    async def request_feeding(self):
        request_data = {
            'animalId': self.animal.animal_id,
            'animalName': self.animal.name,
            'species': self.animal.species,
            'dietaryRequirements': self.animal.dietary_requirements,
            'timestamp': datetime.now().isoformat()
        }

        await self.send_request(
            to=self.coordinator_jid,
            protocol='FeedRequest',
            content=request_data
        )
        self.pending_feed_request = True
        self.logger.info(f"Requested feeding for {self.animal.name}")
    
    async def request_walk(self):
        request_data = {
            'animalId': self.animal.animal_id,
            'animalName': self.animal.name,
            'species': self.animal.species,
            'behavioralNotes': self.animal.behavioral_notes,
            'timestamp': datetime.now().isoformat()
        }

        await self.send_request(
            to=self.coordinator_jid,
            protocol='WalkRequest',
            content=request_data
        )
        self.pending_walk_request = True
        self.logger.info(f"Requested walk for {self.animal.name}")
    
    async def request_health_check(self):
        request_data = {
            'animalId': self.animal.animal_id,
            'animalName': self.animal.name,
            'species': self.animal.species,
            'healthStatus': self.animal.health_status.value,
            'medications': self.animal.medications,
            'timestamp': datetime.now().isoformat()
        }

        await self.send_request(
            to=self.coordinator_jid,
            protocol='HealthRequest',
            content=request_data
        )
        self.pending_health_request = True
        self.logger.info(f"Requested health check for {self.animal.name}")

    async def request_vaccination(self):
        request_data = {
            'animalId': self.animal.animal_id,
            'animalName': self.animal.name,
            'species': self.animal.species,
            'vaccinationType': 'routine',
            'nextDue': self.animal.next_vaccination_due,
            'timestamp': datetime.now().isoformat()
        }

        await self.send_request(
            to=self.coordinator_jid,
            protocol='VaccinationRequest',
            content=request_data
        )
        self.pending_vaccination_request = True
        self.logger.info(f"Requested vaccination for {self.animal.name}")

    def update_feed_state(self):
        self.animal.update_feed_state()
        self.pending_feed_request = False
        self.logger.info(f"{self.animal.name} has been marked as fed")
    
    def update_walk_state(self):
        self.animal.update_walk_state()
        self.pending_walk_request = False
        self.logger.info(f"{self.animal.name} has been marked as walked")
    
    def update_health_state(self, status: str):
        from models.enums import AnimalHealthStatus
        self.animal.update_health_status(AnimalHealthStatus(status))
        self.pending_health_request = False
        self.logger.info(f"{self.animal.name} health status updated to {status}")

    def update_vaccination_state(self, vaccination_type: str):
        # Update vaccination status
        if not self.animal.vaccination_status:
            self.animal.vaccination_status = {}
        self.animal.vaccination_status[vaccination_type] = datetime.now().strftime('%Y-%m-%d')

        # Clear next vaccination due if it was for this type
        self.animal.next_vaccination_due = None

        self.pending_vaccination_request = False
        self.logger.info(f"{self.animal.name} has been vaccinated ({vaccination_type})")

    def update_initial_checkup_state(self, checkup_data: dict):
        from models.enums import AnimalHealthStatus

        # Update health status
        health_status = checkup_data.get('healthStatus', 'healthy')
        self.animal.update_health_status(AnimalHealthStatus(health_status))

        # Update vaccination info if provided
        vaccinations_needed = checkup_data.get('vaccinationsNeeded', [])
        if vaccinations_needed:
            self.logger.info(f"{self.animal.name} needs vaccinations: {', '.join(vaccinations_needed)}")

        # Update adoption status if cleared
        clear_for_adoption = checkup_data.get('clearForAdoption', False)
        if clear_for_adoption:
            from models.enums import AnimalAdoptionStatus
            self.animal.adoption_status = AnimalAdoptionStatus.AVAILABLE
            self.logger.info(f"{self.animal.name} is now available for adoption")

        self.logger.info(f"{self.animal.name} initial checkup complete - Health: {health_status}")
