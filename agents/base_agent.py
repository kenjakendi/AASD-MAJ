from spade.agent import Agent
from spade.message import Message
from spade.template import Template
import json
import time
import asyncio
import os
from typing import Dict, Any, Optional
from datetime import datetime

from config.settings import Settings
from utils.logger import get_logger
from utils.message_builder import MessageBuilder

# Import requests for HTTP communication with dashboard
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Dashboard API endpoint
DASHBOARD_URL = os.getenv('DASHBOARD_URL', 'http://dashboard:5000')


class BaseAgent(Agent):
    
    def __init__(self, jid: str, password: str, config: Optional[Dict] = None,
                 verify_security: bool = False):
        super().__init__(jid, password, verify_security)
        self.config = config or {}
        self.logger = get_logger(self.name)
        self.message_builder = MessageBuilder()
        self.start_time = None
        
    @property
    def name(self) -> str:
        return str(self.jid).split('@')[0]
    
    async def setup(self):
        self.start_time = datetime.now()
        self.logger.info(f"Agent {self.jid} is starting up")
        
        # Register with dashboard via HTTP (run in thread pool to avoid blocking)
        if REQUESTS_AVAILABLE:
            try:
                role = self.config.get('role', 'unknown')
                # Run blocking HTTP request in executor
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: requests.post(
                        f"{DASHBOARD_URL}/api/track_agent",
                        json={
                            'jid': str(self.jid),
                            'role': role,
                            'metadata': self.config
                        },
                        timeout=2
                    )
                )
                if response.status_code == 200:
                    self.logger.info(f"✅ Registered with dashboard")
                else:
                    self.logger.warning(f"❌ Failed to register with dashboard: {response.status_code}")
            except Exception as e:
                self.logger.info(f"⚠️  Dashboard not available: {e}")

    async def _update_tracker_metadata(self):
        if REQUESTS_AVAILABLE:
            try:
                role = self.config.get('role', 'unknown')
                # Run blocking HTTP request in executor
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: requests.post(
                        f"{DASHBOARD_URL}/api/track_agent",
                        json={
                            'jid': str(self.jid),
                            'role': role,
                            'metadata': self.config
                        },
                        timeout=2
                    )
                )
                if response.status_code == 200:
                    self.logger.info(f"✅ Updated metadata in dashboard tracker")
                else:
                    self.logger.warning(f"❌ Failed to update tracker metadata: {response.status_code}")
            except Exception as e:
                self.logger.info(f"⚠️  Could not update tracker metadata: {e}")

    async def start_with_retry(self, max_retries: int = 5, delay: int = 3) -> bool:
        for attempt in range(1, max_retries + 1):
            try:
                await self.start(auto_register=True)
                self.logger.info(f"Agent {self.jid} registered successfully (attempt {attempt})")
                return True
            except Exception as e:
                self.logger.warning(f"Attempt {attempt}/{max_retries} failed: {e}")
                if attempt < max_retries:
                    self.logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    self.logger.error(f"Failed to start agent after {max_retries} attempts")
                    raise
        return False
    
    async def send_message(self, to: str, content: Dict[str, Any], 
                          metadata: Optional[Dict[str, str]] = None) -> None:
        if not self.is_alive():
            self.logger.warning(f"Agent not alive, cannot send message to {to}")
            return
            
        msg = Message(to=to)
        msg.set_metadata("performative", "inform")
        
        if metadata:
            for key, value in metadata.items():
                msg.set_metadata(key, str(value))
        
        msg.body = json.dumps(content, default=str)
        
        # Use SPADE's client to send messages
        try:
            if hasattr(self, 'client') and self.client:
                # SPADE 3.x uses client.send() with prepared message
                await self.client.send(msg.prepare())
                self.logger.debug(f"Sent message to {to}: {content}")
                
                # Track message for visualization via HTTP (fire and forget)
                if REQUESTS_AVAILABLE:
                    try:
                        # Run in background without waiting
                        loop = asyncio.get_event_loop()
                        loop.run_in_executor(
                            None,
                            lambda: requests.post(
                                f"{DASHBOARD_URL}/api/track_message",
                                json={
                                    'from_jid': str(self.jid),
                                    'to_jid': to,
                                    'content': content,
                                    'metadata': metadata or {}
                                },
                                timeout=0.5
                            )
                        )
                    except:
                        pass  # Silently fail if dashboard unavailable
            else:
                self.logger.error("Agent client not available, cannot send message")
        except Exception as e:
            self.logger.error(f"Error sending message to {to}: {e}", exc_info=True)
    
    async def send_request(self, to: str, protocol: str, content: Dict[str, Any]) -> None:
        await self.send_message(
            to=to,
            content=content,
            metadata={
                'protocol': protocol,
                'performative': 'request',
                'timestamp': datetime.now().isoformat()
            }
        )
    
    async def send_confirm(self, to: str, protocol: str, content: Dict[str, Any]) -> None:
        await self.send_message(
            to=to,
            content=content,
            metadata={
                'protocol': protocol,
                'performative': 'confirm',
                'timestamp': datetime.now().isoformat()
            }
        )
    
    async def send_inform(self, to: str, protocol: str, content: Dict[str, Any]) -> None:
        await self.send_message(
            to=to,
            content=content,
            metadata={
                'protocol': protocol,
                'performative': 'inform',
                'timestamp': datetime.now().isoformat()
            }
        )
    
    def get_uptime(self) -> float:
        if self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)
