import json
from spade.behaviour import CyclicBehaviour
from models.enums import Priority


class ReceiveCleanRequestBehaviour(CyclicBehaviour):
    
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            try:
                content = json.loads(msg.body)
                self.agent.logger.info(f"Received clean request: {content}")
                
                priority = Priority.HIGH if content.get('requiresSpecialCleaning') else Priority.NORMAL
                self.agent.add_request('clean', content, priority)
                
            except Exception as e:
                self.agent.logger.error(f"Error processing clean request: {e}")


class ReceiveFeedRequestBehaviour(CyclicBehaviour):
    
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            try:
                content = json.loads(msg.body)
                self.agent.logger.info(f"Received feed request: {content}")
                
                self.agent.add_request('feed', content, Priority.NORMAL)
                
            except Exception as e:
                self.agent.logger.error(f"Error processing feed request: {e}")


class ReceiveWalkRequestBehaviour(CyclicBehaviour):
    
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            try:
                content = json.loads(msg.body)
                self.agent.logger.info(f"Received walk request: {content}")
                
                self.agent.add_request('walk', content, Priority.NORMAL)
                
            except Exception as e:
                self.agent.logger.error(f"Error processing walk request: {e}")


class ReceiveHealthRequestBehaviour(CyclicBehaviour):

    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            try:
                content = json.loads(msg.body)
                self.agent.logger.info(f"Received health request: {content}")

                # Health requests are high priority
                self.agent.add_request('health', content, Priority.HIGH)

            except Exception as e:
                self.agent.logger.error(f"Error processing health request: {e}")


class ReceiveVaccinationRequestBehaviour(CyclicBehaviour):

    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            try:
                content = json.loads(msg.body)
                self.agent.logger.info(f"Received vaccination request: {content}")

                # Vaccination requests are high priority
                self.agent.add_request('vaccination', content, Priority.HIGH)

            except Exception as e:
                self.agent.logger.error(f"Error processing vaccination request: {e}")


class ReceiveNewAnimalBehaviour(CyclicBehaviour):
    
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            try:
                content = json.loads(msg.body)
                self.agent.logger.info(f"Received new animal registration: {content}")
                
                # New animal registrations are urgent (need initial checkup)
                self.agent.add_request('registration', content, Priority.URGENT)
                
            except Exception as e:
                self.agent.logger.error(f"Error processing registration: {e}")


class ReceiveAdoptionApplicationBehaviour(CyclicBehaviour):
    
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            try:
                content = json.loads(msg.body)
                self.agent.logger.info(f"Received adoption application: {content}")
                
                self.agent.add_request('adoption', content, Priority.NORMAL)
                
            except Exception as e:
                self.agent.logger.error(f"Error processing adoption application: {e}")
