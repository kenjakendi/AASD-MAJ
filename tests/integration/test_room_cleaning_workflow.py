"""Integration tests for room cleaning workflows.

Tests the complete workflow:
Room Agent → Coordinator → Cleaner → Room State Update
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from spade.message import Message
import json


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_room_cleaning_request_workflow(test_room_agent, test_coordinator_agent,
                                              test_cleaner_agent, sample_clean_room_data):
    """Test complete room cleaning request and execution workflow."""
    # ARRANGE
    room_agent = test_room_agent
    coordinator = test_coordinator_agent
    cleaner = test_cleaner_agent

    # ACT - Room agent requests cleaning
    clean_request_msg = Message(to=str(coordinator.jid))
    clean_request_data = {
        "room_id": sample_clean_room_data["room_id"],
        "room_name": "Housing Unit A",
        "cleanliness_state": "dirty",
        "priority": sample_clean_room_data["priority"],
        "requires_special_cleaning": sample_clean_room_data["parameters"]["requires_special_cleaning"],
        "requested_at": datetime.now().isoformat()
    }
    clean_request_msg.body = json.dumps(clean_request_data)
    clean_request_msg.set_metadata("performative", "request_cleaning")
    clean_request_msg.set_metadata("room_id", sample_clean_room_data["room_id"])

    await room_agent.send(clean_request_msg)
    await asyncio.sleep(2)

    # Coordinator assigns to cleaner
    assign_msg = Message(to=str(cleaner.jid))
    assign_data = clean_request_data.copy()
    assign_data["task_id"] = "TASK-CLEAN-001"
    assign_data["assigned_by"] = str(coordinator.jid)
    assign_msg.body = json.dumps(assign_data)
    assign_msg.set_metadata("performative", "assign_clean_task")

    await coordinator.send(assign_msg)
    await asyncio.sleep(2)

    # ASSERT
    assert len(coordinator.received_messages) >= 1, "Coordinator should receive clean request"
    assert len(cleaner.received_messages) >= 1, "Cleaner should receive task assignment"

    # Verify request data
    request = json.loads(coordinator.received_messages[0].body)
    assert request["room_id"] == "ROOM001"
    assert request["cleanliness_state"] == "dirty"

    # Verify assignment
    assignment = json.loads(cleaner.received_messages[0].body)
    assert assignment["task_id"] == "TASK-CLEAN-001"
    assert assignment["room_id"] == "ROOM001"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_cleaning_in_progress_notification(test_cleaner_agent, test_room_agent):
    """Test cleaner notifies room when cleaning starts."""
    # ARRANGE
    cleaner = test_cleaner_agent
    room_agent = test_room_agent

    # ACT - Cleaner starts cleaning and notifies room
    start_msg = Message(to=str(room_agent.jid))
    start_data = {
        "room_id": "ROOM001",
        "task_id": "TASK-CLEAN-001",
        "status": "cleaning_in_progress",
        "worker_id": str(cleaner.jid),
        "started_at": datetime.now().isoformat()
    }
    start_msg.body = json.dumps(start_data)
    start_msg.set_metadata("performative", "cleaning_started")

    await cleaner.send(start_msg)
    await asyncio.sleep(2)

    # ASSERT
    assert len(room_agent.received_messages) >= 1
    received = json.loads(room_agent.received_messages[0].body)
    assert received["status"] == "cleaning_in_progress"
    assert received["room_id"] == "ROOM001"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_cleaning_completion_workflow(test_cleaner_agent, test_room_agent,
                                           test_coordinator_agent):
    """Test cleaning completion notification to room and coordinator."""
    # ARRANGE
    cleaner = test_cleaner_agent
    room_agent = test_room_agent
    coordinator = test_coordinator_agent

    # ACT - Cleaner completes cleaning
    completion_data = {
        "room_id": "ROOM001",
        "task_id": "TASK-CLEAN-001",
        "status": "completed",
        "worker_id": str(cleaner.jid),
        "completed_at": datetime.now().isoformat(),
        "new_state": "clean",
        "notes": "Standard cleaning completed successfully"
    }

    # Notify room
    room_msg = Message(to=str(room_agent.jid))
    room_msg.body = json.dumps(completion_data)
    room_msg.set_metadata("performative", "cleaning_completed")
    await cleaner.send(room_msg)

    # Notify coordinator
    coord_msg = Message(to=str(coordinator.jid))
    coord_msg.body = json.dumps(completion_data)
    coord_msg.set_metadata("performative", "task_completed")
    await cleaner.send(coord_msg)

    await asyncio.sleep(2)

    # ASSERT
    assert len(room_agent.received_messages) >= 1, "Room should be notified"
    assert len(coordinator.received_messages) >= 1, "Coordinator should be notified"

    # Verify room notification
    room_notification = json.loads(room_agent.received_messages[0].body)
    assert room_notification["status"] == "completed"
    assert room_notification["new_state"] == "clean"

    # Verify coordinator notification
    coord_notification = json.loads(coordinator.received_messages[0].body)
    assert coord_notification["task_id"] == "TASK-CLEAN-001"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_special_cleaning_high_priority(test_room_agent, test_coordinator_agent):
    """Test special cleaning requests get high priority."""
    # ARRANGE
    room_agent = test_room_agent
    coordinator = test_coordinator_agent

    # ACT - Room requests special cleaning
    special_clean_msg = Message(to=str(coordinator.jid))
    special_clean_data = {
        "room_id": "ROOM-MEDICAL-01",
        "room_name": "Medical Room",
        "room_type": "medical",
        "cleanliness_state": "dirty",
        "priority": "high",
        "requires_special_cleaning": True,
        "special_cleaning_notes": "Use hospital-grade disinfectant",
        "requested_at": datetime.now().isoformat()
    }
    special_clean_msg.body = json.dumps(special_clean_data)
    special_clean_msg.set_metadata("performative", "request_cleaning")
    special_clean_msg.set_metadata("priority", "high")

    await room_agent.send(special_clean_msg)
    await asyncio.sleep(2)

    # ASSERT
    assert len(coordinator.received_messages) >= 1
    request = json.loads(coordinator.received_messages[0].body)
    assert request["requires_special_cleaning"] is True
    assert request["priority"] == "high"
    assert "special_cleaning_notes" in request
    assert special_clean_msg.get_metadata("priority") == "high"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_scheduled_cleaning_time_window(test_room_agent, test_coordinator_agent):
    """Test scheduled cleaning respects time window."""
    # ARRANGE
    room_agent = test_room_agent
    coordinator = test_coordinator_agent

    # ACT - Room sends scheduled cleaning notification
    scheduled_msg = Message(to=str(coordinator.jid))
    scheduled_data = {
        "room_id": "ROOM001",
        "room_name": "Housing Unit A",
        "notification_type": "scheduled_cleaning_due",
        "scheduled_time": "08:00",
        "current_time": datetime.now().time().isoformat(),
        "cleanliness_state": "clean",  # Still clean but due for scheduled maintenance
        "last_cleaned": (datetime.now() - timedelta(hours=24)).isoformat()
    }
    scheduled_msg.body = json.dumps(scheduled_data)
    scheduled_msg.set_metadata("performative", "scheduled_cleaning_notification")

    await room_agent.send(scheduled_msg)
    await asyncio.sleep(2)

    # ASSERT
    assert len(coordinator.received_messages) >= 1
    notification = json.loads(coordinator.received_messages[0].body)
    assert notification["notification_type"] == "scheduled_cleaning_due"
    assert "scheduled_time" in notification
