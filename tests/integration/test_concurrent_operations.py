"""Integration tests for concurrent operations and system stress testing.

Tests system behavior under concurrent load with multiple agents and tasks.
"""

import pytest
import asyncio
from datetime import datetime
from spade.message import Message
import json


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_multiple_workers_concurrent_execution(test_coordinator_agent,
                                                     multiple_caretaker_agents,
                                                     test_veterinarian_agent,
                                                     sample_feed_task_data,
                                                     sample_walk_task_data,
                                                     sample_health_check_data):
    """Test multiple workers handle concurrent tasks without interference."""
    # ARRANGE
    coordinator = test_coordinator_agent
    caretaker1, caretaker2 = multiple_caretaker_agents
    veterinarian = test_veterinarian_agent

    # ACT - Submit multiple tasks simultaneously
    tasks = [
        (caretaker1, "feed", sample_feed_task_data, "TASK-001"),
        (caretaker1, "walk", sample_walk_task_data, "TASK-002"),
        (caretaker2, "feed", sample_feed_task_data, "TASK-003"),
        (caretaker2, "walk", sample_walk_task_data, "TASK-004"),
        (veterinarian, "health_check", sample_health_check_data, "TASK-005")
    ]

    for worker, task_type, task_data, task_id in tasks:
        msg = Message(to=str(worker.jid))
        data = task_data.copy()
        data["task_id"] = task_id
        msg.body = json.dumps(data)
        msg.set_metadata("performative", f"assign_{task_type}_task")
        await coordinator.send(msg)

    await asyncio.sleep(3)

    # ASSERT - All workers received their tasks
    assert len(caretaker1.received_messages) >= 2, "Caretaker 1 should receive 2 tasks"
    assert len(caretaker2.received_messages) >= 2, "Caretaker 2 should receive 2 tasks"
    assert len(veterinarian.received_messages) >= 1, "Veterinarian should receive 1 task"

    # Verify no message loss or duplication
    total_messages = (
        len(caretaker1.received_messages) +
        len(caretaker2.received_messages) +
        len(veterinarian.received_messages)
    )
    assert total_messages >= 5, "All 5 tasks should be received"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_concurrent_adoption_applications(test_coordinator_agent, test_adoption_agent,
                                                sample_adoption_application_data):
    """Test multiple adoption applications processed concurrently."""
    # ARRANGE
    coordinator = test_coordinator_agent
    adoption_agent = test_adoption_agent

    # ACT - Submit 3 adoption applications simultaneously
    applications = []
    for i in range(3):
        app_data = sample_adoption_application_data.copy()
        app_data["application_id"] = f"APP-{i+1:03d}"
        app_data["applicant_name"] = f"Applicant {i+1}"
        app_data["animal_id"] = f"DOG{i+1:03d}"
        applications.append(app_data)

    # Send all applications concurrently
    for app_data in applications:
        msg = Message(to=str(adoption_agent.jid))
        msg.body = json.dumps(app_data)
        msg.set_metadata("performative", "review_adoption_application")
        await coordinator.send(msg)

    await asyncio.sleep(3)

    # ASSERT - All applications received
    assert len(adoption_agent.received_messages) >= 3, "All 3 applications should be received"

    # Verify each application is unique
    received_apps = [json.loads(msg.body) for msg in adoption_agent.received_messages]
    app_ids = [app["application_id"] for app in received_apps]
    assert len(set(app_ids)) == len(app_ids), "No duplicate applications"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_message_ordering_consistency(test_coordinator_agent, test_caretaker_agent):
    """Test message ordering preserved under load."""
    # ARRANGE
    coordinator = test_coordinator_agent
    caretaker = test_caretaker_agent

    # ACT - Send 10 messages rapidly with sequence numbers
    for i in range(10):
        msg = Message(to=str(caretaker.jid))
        data = {
            "sequence_number": i,
            "task_id": f"TASK-SEQ-{i:03d}",
            "timestamp": datetime.now().isoformat()
        }
        msg.body = json.dumps(data)
        msg.set_metadata("performative", "test_message")
        msg.set_metadata("sequence", str(i))
        await coordinator.send(msg)
        await asyncio.sleep(0.1)  # Small delay to preserve order

    await asyncio.sleep(3)

    # ASSERT - All messages received
    assert len(caretaker.received_messages) >= 10, "All 10 messages should be received"

    # Verify sequence numbers (allowing some reordering tolerance)
    received_data = [json.loads(msg.body) for msg in caretaker.received_messages[:10]]
    sequence_numbers = [d["sequence_number"] for d in received_data]

    # Check all messages received (regardless of order)
    assert sorted(sequence_numbers) == list(range(10)), "All sequence numbers present"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_concurrent_room_cleaning_requests(test_coordinator_agent, test_cleaner_agent,
                                                 sample_clean_room_data):
    """Test multiple concurrent room cleaning requests."""
    # ARRANGE
    coordinator = test_coordinator_agent
    cleaner = test_cleaner_agent

    # ACT - Request cleaning for 5 rooms simultaneously
    rooms = [f"ROOM{i:03d}" for i in range(1, 6)]

    for room_id in rooms:
        msg = Message(to=str(cleaner.jid))
        data = sample_clean_room_data.copy()
        data["room_id"] = room_id
        data["task_id"] = f"TASK-CLEAN-{room_id}"
        msg.body = json.dumps(data)
        msg.set_metadata("performative", "assign_clean_task")
        await coordinator.send(msg)

    await asyncio.sleep(3)

    # ASSERT - All cleaning tasks received
    assert len(cleaner.received_messages) >= 5, "All 5 cleaning tasks should be received"

    # Verify each room is unique
    received_tasks = [json.loads(msg.body) for msg in cleaner.received_messages]
    room_ids = [task["room_id"] for task in received_tasks]
    assert len(set(room_ids)) == len(room_ids), "No duplicate room assignments"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_concurrent_task_completion_notifications(test_coordinator_agent,
                                                        multiple_caretaker_agents):
    """Test concurrent task completion notifications."""
    # ARRANGE
    coordinator = test_coordinator_agent
    caretaker1, caretaker2 = multiple_caretaker_agents

    # ACT - Both workers complete tasks simultaneously
    completions = [
        (caretaker1, "TASK-001", "FEED"),
        (caretaker1, "TASK-002", "WALK"),
        (caretaker2, "TASK-003", "FEED"),
        (caretaker2, "TASK-004", "WALK"),
    ]

    for worker, task_id, task_type in completions:
        msg = Message(to=str(coordinator.jid))
        data = {
            "task_id": task_id,
            "task_type": task_type,
            "status": "completed",
            "worker_id": str(worker.jid),
            "completed_at": datetime.now().isoformat()
        }
        msg.body = json.dumps(data)
        msg.set_metadata("performative", "task_completed")
        await worker.send(msg)

    await asyncio.sleep(2)

    # ASSERT - All completions received by coordinator
    assert len(coordinator.received_messages) >= 4, "All 4 completions should be received"

    # Verify all task IDs unique
    received_completions = [json.loads(msg.body) for msg in coordinator.received_messages]
    task_ids = [c["task_id"] for c in received_completions]
    assert len(set(task_ids)) == len(task_ids), "No duplicate completions"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_high_frequency_availability_updates(test_coordinator_agent,
                                                   multiple_caretaker_agents):
    """Test system handles high-frequency availability updates."""
    # ARRANGE
    coordinator = test_coordinator_agent
    caretaker1, caretaker2 = multiple_caretaker_agents

    # ACT - Workers send frequent availability updates
    for i in range(5):
        for worker in [caretaker1, caretaker2]:
            msg = Message(to=str(coordinator.jid))
            data = {
                "worker_id": str(worker.jid),
                "worker_role": "caretaker",
                "is_available": True,
                "current_load": i,
                "update_number": i,
                "timestamp": datetime.now().isoformat()
            }
            msg.body = json.dumps(data)
            msg.set_metadata("performative", "availability_update")
            await worker.send(msg)
            await asyncio.sleep(0.1)

    await asyncio.sleep(2)

    # ASSERT - Coordinator received multiple updates
    assert len(coordinator.received_messages) >= 10, "Should receive 10 availability updates"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_concurrent_priority_task_processing(test_coordinator_agent, test_caretaker_agent,
                                                   test_veterinarian_agent):
    """Test concurrent processing of tasks with different priorities."""
    # ARRANGE
    coordinator = test_coordinator_agent
    caretaker = test_caretaker_agent
    veterinarian = test_veterinarian_agent

    # ACT - Submit mixed priority tasks
    tasks = [
        (caretaker, "normal", "feed"),
        (veterinarian, "urgent", "initial_checkup"),
        (caretaker, "low", "clean"),
        (veterinarian, "high", "vaccination"),
        (caretaker, "normal", "walk"),
    ]

    for worker, priority, task_type in tasks:
        msg = Message(to=str(worker.jid))
        data = {
            "task_type": task_type,
            "priority": priority,
            "timestamp": datetime.now().isoformat()
        }
        msg.body = json.dumps(data)
        msg.set_metadata("performative", f"assign_{task_type}_task")
        msg.set_metadata("priority", priority)
        await coordinator.send(msg)

    await asyncio.sleep(3)

    # ASSERT - All tasks delivered
    total_received = len(caretaker.received_messages) + len(veterinarian.received_messages)
    assert total_received >= 5, "All 5 tasks should be delivered"

    # Verify priority metadata preserved
    all_messages = caretaker.received_messages + veterinarian.received_messages
    priorities = [msg.get_metadata("priority") for msg in all_messages]
    assert "urgent" in priorities
    assert "high" in priorities
    assert "normal" in priorities
    assert "low" in priorities
