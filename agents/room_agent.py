from typing import Dict
from datetime import datetime

from spade.template import Template

from agents.base_agent import BaseAgent
from models.room import Room
from behaviours.room.monitor_cleanliness_behaviour import MonitorCleanlinessBehaviour
from behaviours.room.receive_clean_confirmation_behaviour import ReceiveCleanConfirmationBehaviour
from config.settings import Settings


class RoomAgent(BaseAgent):
    
    def __init__(self, jid: str, password: str, room_data: Dict):
        super().__init__(jid, password, room_data)
        self.room = Room.from_dict(room_data)
        self.coordinator_jid = f"coordinator@{Settings.XMPP_SERVER}"
    
    async def setup(self):
        await super().setup()
        
        self.logger.info(f"Setting up Room Agent for: {self.room.name} ({self.room.room_id})")
        
        # Behaviour 1: Monitor Cleanliness (Periodic)
        self.add_behaviour(MonitorCleanlinessBehaviour(period=Settings.CLEAN_CHECK_INTERVAL))
        
        # Behaviour 2: Receive Clean Confirmations
        confirmation_template = Template()
        confirmation_template.set_metadata("protocol", "ConfirmCleanTask")
        self.add_behaviour(ReceiveCleanConfirmationBehaviour(), confirmation_template)
        
        self.logger.info(f"Room Agent for {self.room.name} is ready")
    
    def needs_cleaning(self) -> bool:
        return self.room.needs_cleaning()
    
    def is_scheduled_for_cleaning(self) -> bool:
        return self.room.is_scheduled_for_cleaning()
    
    async def request_cleaning(self):
        request_data = {
            'roomId': self.room.room_id,
            'roomName': self.room.name,
            'roomType': self.room.room_type.value,
            'requiresSpecialCleaning': self.room.requires_special_cleaning,
            'specialCleaningNotes': self.room.special_cleaning_notes,
            'currentState': self.room.cleanliness_state.value,
            'timestamp': datetime.now().isoformat()
        }
        
        await self.send_request(
            to=self.coordinator_jid,
            protocol='CleanRequest',
            content=request_data
        )
        
        # Mark as cleaning in progress
        self.room.mark_cleaning_in_progress()
        self.logger.info(f"Requested cleaning for {self.room.name}")
    
    def mark_clean(self):
        self.room.mark_clean()
        self.logger.info(f"{self.room.name} has been marked as clean")
