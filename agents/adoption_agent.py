from typing import Dict, List
from datetime import datetime
import asyncio

from spade.template import Template

from agents.base_agent import BaseAgent
from models.adoption_application import AdoptionApplication, ApplicationStatus
from behaviours.adoption.receive_application_behaviour import ReceiveApplicationBehaviour
from behaviours.adoption.process_adoption_behaviour import ProcessAdoptionBehaviour
from config.settings import Settings


class AdoptionAgent(BaseAgent):
    
    def __init__(self, jid: str, password: str, config: Dict):
        super().__init__(jid, password, config)
        self.coordinator_jid = Settings.get_coordinator_jid()
        self.processing_interval = config.get('processing_interval', 60)
        self.application_review_time = config.get('application_review_time', 300)
        self.adoption_criteria = config.get('adoption_criteria', {})
        self.adoption_fees = config.get('adoption_fee', {})
        
        # Application tracking
        self.pending_applications: List[AdoptionApplication] = []
        self.approved_applications: List[AdoptionApplication] = []
        self.rejected_applications: List[AdoptionApplication] = []
        self.completed_adoptions: List[AdoptionApplication] = []
    
    async def setup(self):
        await super().setup()
        
        self.logger.info("Setting up Adoption Agent")
        
        # Behaviour 1: Receive Applications
        application_template = Template()
        application_template.set_metadata("protocol", "AdoptionApplicationTask")
        self.add_behaviour(ReceiveApplicationBehaviour(), application_template)
        
        # Behaviour 2: Process Adoptions (Periodic)
        self.add_behaviour(ProcessAdoptionBehaviour(period=self.processing_interval))
        
        self.logger.info("Adoption Agent is ready")
    
    async def receive_application(self, application_data: Dict) -> str:
        application = AdoptionApplication.from_dict(application_data)
        
        self.logger.info(f"Received adoption application {application.application_id} " +
                        f"for animal {application.animal_id} from {application.applicant_name}")
        
        # Start review process
        application.start_review()
        self.pending_applications.append(application)
        
        return application.application_id
    
    async def review_application(self, application: AdoptionApplication) -> bool:
        self.logger.info(f"Reviewing application {application.application_id}")
        
        # Simulate review time
        await asyncio.sleep(self.application_review_time)
        
        # Check criteria
        criteria = self.adoption_criteria
        
        # Age check
        if application.applicant_age < criteria.get('min_age', 21):
            application.reject("Applicant does not meet minimum age requirement")
            self.rejected_applications.append(application)
            self.logger.info(f"Application {application.application_id} rejected: age requirement")
            return False
        
        # Reference check (if required)
        if criteria.get('requires_reference', True) and not application.references:
            application.reject("Missing required references")
            self.rejected_applications.append(application)
            self.logger.info(f"Application {application.application_id} rejected: missing references")
            return False
        
        # Approve application
        application.approve("Application meets all criteria")
        self.approved_applications.append(application)
        self.logger.info(f"Application {application.application_id} approved")
        
        return True
    
    async def finalize_adoption(self, application: AdoptionApplication):
        self.logger.info(f"Finalizing adoption for animal {application.animal_id}")
        
        # Mark application as completed
        application.complete()
        self.completed_adoptions.append(application)
        
        # Prepare adoption data
        adoption_data = {
            'applicationId': application.application_id,
            'animalId': application.animal_id,
            'applicantId': application.applicant_id,
            'applicantName': application.applicant_name,
            'adoptionDate': datetime.now().isoformat(),
            'status': 'adopted'
        }
        
        # 1. Notify coordinator
        await self.send_confirm(
            to=self.coordinator_jid,
            protocol='ConfirmAdoptionApplicationTask',
            content=adoption_data
        )
        
        # 2. Notify the animal (update adoption status)
        animal_jid = f"animal_{application.animal_id}@{Settings.XMPP_SERVER}"
        await self.send_inform(
            to=animal_jid,
            protocol='UpdateAdoptionStatus',
            content={
                'animalId': application.animal_id,
                'adoptionStatus': 'adopted',
                'adoptedBy': application.applicant_name,
                'adoptionDate': datetime.now().isoformat()
            }
        )
        self.logger.info(f"Notified animal {application.animal_id} about adoption")
        
        # 3. Notify the applicant (adoption approved)
        applicant_jid = f"applicant_{application.applicant_id}@{Settings.XMPP_SERVER}"
        await self.send_confirm(
            to=applicant_jid,
            protocol='ConfirmAdoptionApplicationTask',
            content={
                'applicationId': application.application_id,
                'animalId': application.animal_id,
                'status': 'adopted',
                'message': f"Congratulations! Your application to adopt animal {application.animal_id} has been approved.",
                'nextSteps': 'Please contact the shelter to complete the adoption process.',
                'adoptionFee': self.adoption_fees.get(application.animal_id, 0)
            }
        )
        self.logger.info(f"Notified applicant {application.applicant_id} about adoption approval")
        
        self.logger.info(f"Adoption finalized for animal {application.animal_id}")
    
    def get_statistics(self) -> Dict:
        return {
            'pending_applications': len(self.pending_applications),
            'approved_applications': len(self.approved_applications),
            'rejected_applications': len(self.rejected_applications),
            'completed_adoptions': len(self.completed_adoptions),
            'total_applications': (len(self.pending_applications) + 
                                 len(self.approved_applications) + 
                                 len(self.rejected_applications) + 
                                 len(self.completed_adoptions))
        }
