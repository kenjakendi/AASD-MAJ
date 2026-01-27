"""Integration test fixtures for SPADE agent testing.

This module provides fixtures for managing SPADE agent lifecycle,
XMPP connections, and test data for integration tests.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
from spade.template import Template
from spade.xmpp_client import XMPPClient

# XMPP configuration from docker-compose.yml
XMPP_SERVER = "localhost"  # Use localhost since Docker exposes port to host
XMPP_PORT = 5222
AGENT_PASSWORD = "shelter123"
TEST_TIMEOUT = 30  # seconds


class InsecureXMPPClient(XMPPClient):
    """XMPPClient that allows PLAIN auth without TLS for testing."""

    def __init__(self, jid, password, verify_security, auto_register):
        super().__init__(jid, password, verify_security, auto_register)
        # Allow PLAIN mechanism without TLS
        self['feature_mechanisms'].unencrypted_plain = True


class MessageCollector:
    """Utility class to collect and verify messages sent between agents."""

    def __init__(self):
        self.messages: List[Message] = []
        self.message_types: Dict[str, int] = {}

    def add_message(self, msg: Message):
        """Add a message to the collection."""
        self.messages.append(msg)
        msg_type = msg.metadata.get('performative', 'unknown')
        self.message_types[msg_type] = self.message_types.get(msg_type, 0) + 1

    def count(self, message_type: str) -> int:
        """Count messages of a specific type."""
        return self.message_types.get(message_type, 0)

    def get_messages_by_type(self, message_type: str) -> List[Message]:
        """Get all messages of a specific type."""
        return [
            msg for msg in self.messages
            if msg.metadata.get('performative') == message_type
        ]

    def clear(self):
        """Clear all collected messages."""
        self.messages.clear()
        self.message_types.clear()


class TestAgent(Agent):
    """Base test agent with message collection capabilities."""

    def __init__(self, jid: str, password: str, collector: MessageCollector = None):
        super().__init__(jid, password)
        self.collector = collector or MessageCollector()
        self.received_messages: List[Message] = []

    async def send(self, msg: Message) -> None:
        """Send a message through the XMPP client."""
        import json
        if not msg.sender:
            msg.sender = str(self.jid)

        # Encode body and metadata together as JSON
        envelope = {
            "body": msg.body,
            "metadata": dict(msg.metadata)
        }

        # Convert SPADE Message to slixmpp message
        stanza = self.client.make_message(
            mto=msg.to,
            mfrom=str(self.jid),
            mbody=json.dumps(envelope),
        )
        stanza.send()

    async def _async_start(self, auto_register: bool = True) -> None:
        """Override to use InsecureXMPPClient for testing."""
        await self._hook_plugin_before_connection()

        # Use InsecureXMPPClient instead of regular XMPPClient
        self.client = InsecureXMPPClient(
            self.jid, self.password, self.verify_security, auto_register
        )
        # Presence service
        from spade.presence import PresenceManager
        self.presence = PresenceManager(agent=self, approve_all=False)

        await self._async_connect()

        await self._hook_plugin_after_connection()

        await self.setup()
        self._alive.set()
        from spade.behaviour import FSMBehaviour
        for behaviour in self.behaviours:
            if not behaviour.is_running:
                behaviour.set_agent(self)
                if issubclass(type(behaviour), FSMBehaviour):
                    for _, state in behaviour.get_states().items():
                        state.set_agent(self)
                behaviour.start()

    async def setup(self):
        """Agent setup with message collection behavior."""
        import json

        class CollectMessagesBehaviour(CyclicBehaviour):
            async def run(inner_self):
                msg = await inner_self.receive(timeout=1)
                if msg:
                    # Try to decode envelope with metadata
                    try:
                        envelope = json.loads(msg.body)
                        if isinstance(envelope, dict) and "metadata" in envelope:
                            # Restore metadata from envelope
                            for key, value in envelope.get("metadata", {}).items():
                                msg.set_metadata(key, value)
                            # Restore original body
                            msg.body = envelope.get("body", msg.body)
                    except (json.JSONDecodeError, TypeError):
                        pass  # Not an envelope, use message as-is

                    self.received_messages.append(msg)
                    if self.collector:
                        self.collector.add_message(msg)

        self.add_behaviour(CollectMessagesBehaviour())


@pytest.fixture
def message_collector():
    """Create a message collector for test verification."""
    return MessageCollector()


@pytest.fixture
def integration_timeout():
    """Timeout for integration tests (30 seconds)."""
    return TEST_TIMEOUT


@pytest.fixture
def xmpp_config():
    """XMPP connection configuration."""
    return {
        "server": XMPP_SERVER,
        "port": XMPP_PORT,
        "password": AGENT_PASSWORD
    }


@pytest.fixture
async def test_coordinator_agent(xmpp_config, message_collector):
    """Create and start a test coordinator agent."""
    jid = f"test_coordinator_{datetime.now().timestamp()}@{xmpp_config['server']}"
    agent = TestAgent(jid, xmpp_config['password'], message_collector)

    await agent.start(auto_register=True)
    await asyncio.sleep(1)  # Wait for agent startup

    yield agent

    await agent.stop()
    await asyncio.sleep(0.5)  # Wait for cleanup


@pytest.fixture
async def test_caretaker_agent(xmpp_config, message_collector):
    """Create and start a test caretaker agent."""
    jid = f"test_caretaker_{datetime.now().timestamp()}@{xmpp_config['server']}"
    agent = TestAgent(jid, xmpp_config['password'], message_collector)

    await agent.start(auto_register=True)
    await asyncio.sleep(1)

    yield agent

    await agent.stop()
    await asyncio.sleep(0.5)


@pytest.fixture
async def test_veterinarian_agent(xmpp_config, message_collector):
    """Create and start a test veterinarian agent."""
    jid = f"test_vet_{datetime.now().timestamp()}@{xmpp_config['server']}"
    agent = TestAgent(jid, xmpp_config['password'], message_collector)

    await agent.start(auto_register=True)
    await asyncio.sleep(1)

    yield agent

    await agent.stop()
    await asyncio.sleep(0.5)


@pytest.fixture
async def test_cleaner_agent(xmpp_config, message_collector):
    """Create and start a test cleaner agent."""
    jid = f"test_cleaner_{datetime.now().timestamp()}@{xmpp_config['server']}"
    agent = TestAgent(jid, xmpp_config['password'], message_collector)

    await agent.start(auto_register=True)
    await asyncio.sleep(1)

    yield agent

    await agent.stop()
    await asyncio.sleep(0.5)


@pytest.fixture
async def test_adoption_agent(xmpp_config, message_collector):
    """Create and start a test adoption agent."""
    jid = f"test_adoption_{datetime.now().timestamp()}@{xmpp_config['server']}"
    agent = TestAgent(jid, xmpp_config['password'], message_collector)

    await agent.start(auto_register=True)
    await asyncio.sleep(1)

    yield agent

    await agent.stop()
    await asyncio.sleep(0.5)


@pytest.fixture
async def test_animal_agent(xmpp_config, message_collector):
    """Create and start a test animal agent."""
    jid = f"test_animal_{datetime.now().timestamp()}@{xmpp_config['server']}"
    agent = TestAgent(jid, xmpp_config['password'], message_collector)

    await agent.start(auto_register=True)
    await asyncio.sleep(1)

    yield agent

    await agent.stop()
    await asyncio.sleep(0.5)


@pytest.fixture
async def test_room_agent(xmpp_config, message_collector):
    """Create and start a test room agent."""
    jid = f"test_room_{datetime.now().timestamp()}@{xmpp_config['server']}"
    agent = TestAgent(jid, xmpp_config['password'], message_collector)

    await agent.start(auto_register=True)
    await asyncio.sleep(1)

    yield agent

    await agent.stop()
    await asyncio.sleep(0.5)


@pytest.fixture
async def test_applicant_agent(xmpp_config, message_collector):
    """Create and start a test applicant agent."""
    jid = f"test_applicant_{datetime.now().timestamp()}@{xmpp_config['server']}"
    agent = TestAgent(jid, xmpp_config['password'], message_collector)

    await agent.start(auto_register=True)
    await asyncio.sleep(1)

    yield agent

    await agent.stop()
    await asyncio.sleep(0.5)


@pytest.fixture
async def multiple_caretaker_agents(xmpp_config, message_collector):
    """Create and start multiple caretaker agents for load testing."""
    agents = []

    for i in range(2):
        jid = f"test_caretaker_{i}_{datetime.now().timestamp()}@{xmpp_config['server']}"
        agent = TestAgent(jid, xmpp_config['password'], message_collector)
        await agent.start(auto_register=True)
        await asyncio.sleep(0.5)
        agents.append(agent)

    yield agents

    for agent in agents:
        await agent.stop()
    await asyncio.sleep(0.5)


@pytest.fixture
def sample_feed_task_data():
    """Sample feed task data for testing."""
    return {
        "task_type": "feed",
        "animal_id": "DOG001",
        "priority": "normal",
        "parameters": {
            "food_type": "dry_kibble",
            "amount_grams": 500
        }
    }


@pytest.fixture
def sample_walk_task_data():
    """Sample walk task data for testing."""
    return {
        "task_type": "walk",
        "animal_id": "DOG002",
        "priority": "normal",
        "parameters": {
            "duration_minutes": 30
        }
    }


@pytest.fixture
def sample_health_check_data():
    """Sample health check task data for testing."""
    return {
        "task_type": "health_check",
        "animal_id": "CAT001",
        "priority": "high",
        "parameters": {
            "check_type": "routine"
        }
    }


@pytest.fixture
def sample_vaccination_data():
    """Sample vaccination task data for testing."""
    return {
        "task_type": "vaccination",
        "animal_id": "DOG003",
        "priority": "urgent",
        "parameters": {
            "vaccine_type": "rabies"
        }
    }


@pytest.fixture
def sample_clean_room_data():
    """Sample room cleaning task data for testing."""
    return {
        "task_type": "clean",
        "room_id": "ROOM001",
        "priority": "normal",
        "parameters": {
            "requires_special_cleaning": False
        }
    }


@pytest.fixture
def sample_adoption_application_data():
    """Sample adoption application data for testing."""
    return {
        "applicant_name": "John Doe",
        "applicant_age": 30,
        "animal_id": "DOG001",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "address": "123 Main St, City, State 12345",
        "household_size": 3,
        "has_yard": True,
        "has_other_pets": False,
        "references": ["Reference 1", "Reference 2"],
        "reason_for_adoption": "Looking for a family companion"
    }


@pytest.fixture
def sample_initial_checkup_data():
    """Sample initial checkup task data for testing."""
    return {
        "task_type": "initial_checkup",
        "animal_id": "DOG004",
        "priority": "urgent",
        "parameters": {
            "registration_date": datetime.now().isoformat()
        }
    }


async def wait_for_message(agent: TestAgent, timeout: float = 5.0) -> Message:
    """Wait for an agent to receive a message with timeout.

    Args:
        agent: The agent to check for messages
        timeout: Maximum time to wait in seconds

    Returns:
        The received message or None if timeout
    """
    start_time = asyncio.get_event_loop().time()

    while asyncio.get_event_loop().time() - start_time < timeout:
        if agent.received_messages:
            return agent.received_messages.pop(0)
        await asyncio.sleep(0.1)

    return None


async def wait_for_condition(condition_func, timeout: float = 5.0, check_interval: float = 0.1):
    """Wait for a condition to be true with timeout.

    Args:
        condition_func: Callable that returns True when condition is met
        timeout: Maximum time to wait in seconds
        check_interval: Time between condition checks

    Returns:
        True if condition met, False if timeout
    """
    start_time = asyncio.get_event_loop().time()

    while asyncio.get_event_loop().time() - start_time < timeout:
        if condition_func():
            return True
        await asyncio.sleep(check_interval)

    return False


@pytest.fixture
def wait_for_message_helper():
    """Provide the wait_for_message helper function."""
    return wait_for_message


@pytest.fixture
def wait_for_condition_helper():
    """Provide the wait_for_condition helper function."""
    return wait_for_condition
