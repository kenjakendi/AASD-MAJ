"""Integration tests for task assignment workflows.

Tests the complete workflow:
Coordinator → Worker → Task Execution → Completion
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from spade.message import Message
import json


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_basic_agent_communication(test_coordinator_agent, test_caretaker_agent,
                                         wait_for_message_helper):
    """Test basic message passing between two agents."""
    # ARRANGE
    coordinator = test_coordinator_agent
    caretaker = test_caretaker_agent

    # ACT - Send message from coordinator to caretaker
    msg = Message(to=str(caretaker.jid))
    msg.body = json.dumps({"test": "message", "timestamp": datetime.now().isoformat()})
    msg.set_metadata("performative", "test_message")

    await coordinator.send(msg)
    await asyncio.sleep(2)  # Allow message delivery

    # ASSERT
    received_msg = await wait_for_message_helper(caretaker, timeout=3.0)
    assert received_msg is not None, "Caretaker should receive message"
    # Compare bare JID (without resource)
    assert str(coordinator.jid) in str(received_msg.sender)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_feed_task_request_workflow(test_coordinator_agent, test_caretaker_agent,
                                          sample_feed_task_data, message_collector):
    """Test complete feed task workflow: request → assignment → completion."""
    # ARRANGE
    coordinator = test_coordinator_agent
    caretaker = test_caretaker_agent

    # ACT - Coordinator sends feed task assignment to caretaker
    task_msg = Message(to=str(caretaker.jid))
    task_msg.body = json.dumps(sample_feed_task_data)
    task_msg.set_metadata("performative", "assign_feed_task")
    task_msg.set_metadata("task_id", "TASK-FEED-001")

    await coordinator.send(task_msg)
    await asyncio.sleep(2)

    # Caretaker acknowledges receipt
    ack_msg = Message(to=str(coordinator.jid))
    ack_msg.body = json.dumps({
        "task_id": "TASK-FEED-001",
        "status": "acknowledged",
        "worker_id": str(caretaker.jid)
    })
    ack_msg.set_metadata("performative", "task_acknowledged")

    await caretaker.send(ack_msg)
    await asyncio.sleep(2)

    # ASSERT
    assert len(caretaker.received_messages) >= 1, "Caretaker should receive task assignment"
    assert len(coordinator.received_messages) >= 1, "Coordinator should receive acknowledgment"

    # Verify message flow
    assert message_collector.count("assign_feed_task") >= 1
    assert message_collector.count("task_acknowledged") >= 1


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_walk_task_request_workflow(test_coordinator_agent, test_caretaker_agent,
                                          sample_walk_task_data):
    """Test walk task workflow for dogs."""
    # ARRANGE
    coordinator = test_coordinator_agent
    caretaker = test_caretaker_agent

    # ACT - Send walk task
    task_msg = Message(to=str(caretaker.jid))
    task_msg.body = json.dumps(sample_walk_task_data)
    task_msg.set_metadata("performative", "assign_walk_task")
    task_msg.set_metadata("task_id", "TASK-WALK-001")

    await coordinator.send(task_msg)
    await asyncio.sleep(2)

    # ASSERT
    assert len(caretaker.received_messages) >= 1
    received = caretaker.received_messages[0]
    task_data = json.loads(received.body)
    assert task_data["task_type"] == "walk"
    assert task_data["animal_id"] == "DOG002"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_task_completion_notification(test_coordinator_agent, test_caretaker_agent,
                                            sample_feed_task_data):
    """Test task completion notification from worker to coordinator."""
    # ARRANGE
    coordinator = test_coordinator_agent
    caretaker = test_caretaker_agent

    # ACT - Simulate task completion
    completion_msg = Message(to=str(coordinator.jid))
    completion_data = {
        "task_id": "TASK-FEED-001",
        "status": "completed",
        "worker_id": str(caretaker.jid),
        "completion_time": datetime.now().isoformat(),
        "result": {
            "animal_id": sample_feed_task_data["animal_id"],
            "food_consumed": True,
            "notes": "Animal ate all food"
        }
    }
    completion_msg.body = json.dumps(completion_data)
    completion_msg.set_metadata("performative", "task_completed")

    await caretaker.send(completion_msg)
    await asyncio.sleep(2)

    # ASSERT
    assert len(coordinator.received_messages) >= 1
    received = coordinator.received_messages[0]
    assert received.get_metadata("performative") == "task_completed"
    result = json.loads(received.body)
    assert result["status"] == "completed"
    assert result["task_id"] == "TASK-FEED-001"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_multiple_workers_concurrent_tasks(test_coordinator_agent,
                                                 multiple_caretaker_agents,
                                                 sample_feed_task_data):
    """Test coordinator distributing tasks to multiple workers."""
    # ARRANGE
    coordinator = test_coordinator_agent
    caretaker1, caretaker2 = multiple_caretaker_agents

    # ACT - Send two tasks simultaneously
    task1_msg = Message(to=str(caretaker1.jid))
    task1_data = sample_feed_task_data.copy()
    task1_data["animal_id"] = "DOG001"
    task1_msg.body = json.dumps(task1_data)
    task1_msg.set_metadata("performative", "assign_feed_task")
    task1_msg.set_metadata("task_id", "TASK-001")

    task2_msg = Message(to=str(caretaker2.jid))
    task2_data = sample_feed_task_data.copy()
    task2_data["animal_id"] = "DOG002"
    task2_msg.body = json.dumps(task2_data)
    task2_msg.set_metadata("performative", "assign_feed_task")
    task2_msg.set_metadata("task_id", "TASK-002")

    await coordinator.send(task1_msg)
    await coordinator.send(task2_msg)
    await asyncio.sleep(3)

    # ASSERT
    assert len(caretaker1.received_messages) >= 1, "Caretaker 1 should receive task"
    assert len(caretaker2.received_messages) >= 1, "Caretaker 2 should receive task"

    # Verify each got different tasks
    task1_received = json.loads(caretaker1.received_messages[0].body)
    task2_received = json.loads(caretaker2.received_messages[0].body)
    assert task1_received["animal_id"] != task2_received["animal_id"]


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_task_failure_notification(test_coordinator_agent, test_caretaker_agent):
    """Test worker reporting task failure to coordinator."""
    # ARRANGE
    coordinator = test_coordinator_agent
    caretaker = test_caretaker_agent

    # ACT - Simulate task failure
    failure_msg = Message(to=str(coordinator.jid))
    failure_data = {
        "task_id": "TASK-FEED-999",
        "status": "failed",
        "worker_id": str(caretaker.jid),
        "failure_time": datetime.now().isoformat(),
        "error": {
            "code": "ANIMAL_NOT_FOUND",
            "message": "Animal DOG999 not found in system"
        }
    }
    failure_msg.body = json.dumps(failure_data)
    failure_msg.set_metadata("performative", "task_failed")

    await caretaker.send(failure_msg)
    await asyncio.sleep(2)

    # ASSERT
    assert len(coordinator.received_messages) >= 1
    received = coordinator.received_messages[0]
    assert received.get_metadata("performative") == "task_failed"
    result = json.loads(received.body)
    assert result["status"] == "failed"
    assert "error" in result
    assert result["error"]["code"] == "ANIMAL_NOT_FOUND"
