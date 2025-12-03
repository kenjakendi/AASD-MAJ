from spade.behaviour import PeriodicBehaviour


class ProcessAdoptionBehaviour(PeriodicBehaviour):
    
    async def run(self):
        
        # Process pending applications
        for application in list(self.agent.pending_applications):
            # Review application
            approved = await self.agent.review_application(application)
            
            # Remove from pending
            self.agent.pending_applications.remove(application)
            
            # If approved, finalize adoption
            if approved:
                await self.agent.finalize_adoption(application)
