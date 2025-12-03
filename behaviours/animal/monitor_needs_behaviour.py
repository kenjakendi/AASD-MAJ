from spade.behaviour import PeriodicBehaviour


class MonitorNeedsBehaviour(PeriodicBehaviour):
    
    async def run(self):

        # Ensure agent is alive before sending messages
        if not self.agent.is_alive():
            return

        # Don't request care if animal is adopted
        from models.enums import AnimalAdoptionStatus
        if self.agent.animal.adoption_status == AnimalAdoptionStatus.ADOPTED:
            return

        # Check feeding needs (only if no pending request)
        if self.agent.needs_feeding() and not self.agent.pending_feed_request:
            await self.agent.request_feeding()

        # Check walking needs (for dogs, only if no pending request)
        if self.agent.needs_walk() and not self.agent.pending_walk_request:
            await self.agent.request_walk()

        # Check health needs (only if no pending request)
        if self.agent.needs_health_check() and not self.agent.pending_health_request:
            await self.agent.request_health_check()

        # Check vaccination needs (only if no pending request)
        if self.agent.needs_vaccination() and not self.agent.pending_vaccination_request:
            await self.agent.request_vaccination()
