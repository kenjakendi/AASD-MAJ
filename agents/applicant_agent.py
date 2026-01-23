"""
Applicant Agent - Represents a person applying for adoption
Submits adoption applications
"""
    
from typing import Dict
from datetime import datetime
import uuid

from spade.template import Template

from agents.base_agent import BaseAgent
from models.adoption_application import AdoptionApplication, ApplicationStatus
from behaviours.applicant.submit_application_behaviour import SubmitApplicationBehaviour
from config.settings import Settings


class ApplicantAgent(BaseAgent):
    """
    Applicant Agent
    Represents a person interested in adopting an animal:
    - Browses available animals
    - Submits adoption applications
    - Receives application status updates
    """
    
    def __init__(self, jid: str, password: str, applicant_data: Dict):
        super().__init__(jid, password, applicant_data)
        self.applicant_id = applicant_data['id']
        self.applicant_name = applicant_data.get('name', f"Applicant_{self.applicant_id}")
        self.applicant_age = applicant_data.get('age', 25)
        self.applicant_contact = applicant_data.get('contact', '')
        self.applicant_address = applicant_data.get('address', '')
        self.preferred_animals = applicant_data.get('preferred_animals', [])
        
        self.coordinator_jid = Settings.get_coordinator_jid()
        self.adoption_jid = Settings.get_adoption_jid()
        
        self.submitted_applications = []
    
    async def setup(self):
        """Setup applicant agent and behaviours"""
        await super().setup()
        
        self.logger.info(f"Setting up Applicant Agent: {self.applicant_name}")
        
        # Behaviour 1: Receive confirmation messages
        confirmation_template = Template()
        confirmation_template.set_metadata("protocol", "ConfirmAdoptionApplicationTask")
        self.add_behaviour(self._create_receive_confirmation_behaviour(), confirmation_template)
        
        # Behaviour 2: Periodically submit adoption applications (if enabled)
        submission_config = self.config.get('submission_config', {})
        if submission_config.get('enabled', False):
            interval = submission_config.get('interval', 180)  # Default 3 minutes
            self.add_behaviour(SubmitApplicationBehaviour(period=interval))
            self.logger.info(f"Enabled periodic application submission (interval: {interval}s)")
        
        self.logger.info(f"Applicant {self.applicant_name} is ready")
    
    def _create_receive_confirmation_behaviour(self):
        """Create a simple behaviour to receive confirmations"""
        from spade.behaviour import CyclicBehaviour
        
        class ReceiveConfirmationBehaviour(CyclicBehaviour):
            async def run(self):
                msg = await self.receive(timeout=10)
                if msg:
                    import json
                    try:
                        content = json.loads(msg.body)
                        agent = self.agent
                        agent.logger.info(f"Received adoption confirmation: {content}")
                        
                        if content.get('status') == 'adopted':
                            agent.logger.info(f"Adoption approved for animal {content.get('animalId')}!")
                    except Exception as e:
                        agent.logger.error(f"Error processing confirmation: {e}")
        
        return ReceiveConfirmationBehaviour()
    
    async def submit_adoption_application(self, animal_id: str, 
                                         additional_info: Dict = None) -> str:
        """
        Submit an adoption application
        
        Args:
            animal_id: ID of animal to adopt
            additional_info: Additional application information
            
        Returns:
            Application ID
        """
        application_id = f"APP_{str(uuid.uuid4())[:8].upper()}"
        
        info = additional_info or {}
        
        application_data = {
            'application_id': application_id,
            'applicant_id': self.applicant_id,
            'animal_id': animal_id,
            'applicant_name': self.applicant_name,
            'applicant_age': self.applicant_age,
            'applicant_contact': self.applicant_contact,
            'applicant_address': self.applicant_address,
            'has_previous_pet_experience': info.get('has_previous_pet_experience', True),
            'home_type': info.get('home_type', 'house'),
            'has_yard': info.get('has_yard', True),
            'other_pets': info.get('other_pets', []),
            'household_members': info.get('household_members', 2),
            'employment_status': info.get('employment_status', 'employed'),
            'references': info.get('references', ['Reference 1', 'Reference 2']),
            'submitted_at': datetime.now().isoformat()
        }
        
        # Send application to coordinator
        await self.send_request(
            to=self.coordinator_jid,
            protocol='AdoptionApplicationRequest',
            content=application_data
        )
        
        self.submitted_applications.append(application_id)
        self.logger.info(f"Submitted adoption application {application_id} for animal {animal_id}")
        
        return application_id
    
    def is_interested_in(self, animal_species: str) -> bool:
        """Check if applicant is interested in this animal species"""
        if not self.preferred_animals:
            return True
        return animal_species.lower() in [a.lower() for a in self.preferred_animals]

