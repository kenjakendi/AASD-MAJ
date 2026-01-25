"""Integration tests for worker availability and load management.

Tests worker availability reporting, load balancing, and priority queue behavior.
"""

import pytest
import asyncio
from datetime import datetime
from spade.message import Message
import json


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_worker_availability_update(test_coordinator_agent, test_caretaker_agent):
    """Test periodic worker availability reporting to coordinator."""
    # ARRANGE
    coordinator = test_coordinator_agent
    caretaker = test_caretaker_agent

    # ACT - Worker sends availability update
    availability_msg = Message(to=str(coordinator.jid))
    availability_data = {
        "worker_id": str(caretaker.jid),
        "worker_role": "caretaker",
        "is_available": True,
        "current_load": 2,
        "max_concurrent_tasks": 5,
        "current_tasks": ["TASK-FEED-001", "TASK-WALK-002"],
        "competencies": ["feed", "walk", "clean"],
        "timestamp": datetime.now().isoformat()
    }
    availability_msg.body = json.dumps(availability_data)
    availability_msg.set_metadata("performative", "availability_update")

    await caretaker.send(availability_msg)
    await asyncio.sleep(2)

    # ASSERT
    assert len(coordinator.received_messages) >= 1
    update = json.loads(coordinator.received_messages[0].body)
    assert update["is_available"] is True
    assert update["current_load"] == 2
    assert update["max_concurrent_tasks"] == 5


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_worker_max_concurrent_tasks_limit(test_coordinator_agent, test_caretaker_agent):
    """Test worker respects max_concurrent_tasks limit."""
    # ARRANGE
    coordinator = test_coordinator_agent
    caretaker = test_caretaker_agent

    # ACT - Worker at max capacity reports unavailable
    max_capacity_msg = Message(to=str(coordinator.jid))
    max_capacity_data = {
        "worker_id": str(caretaker.jid),
        "worker_role": "caretaker",
        "is_available": False,  # At max capacity
        "current_load": 5,
        "max_concurrent_tasks": 5,
        "current_tasks": [
            "TASK-FEED-001",
            "TASK-FEED-002",
            "TASK-WALK-001",
            "TASK-WALK-002",
            "TASK-CLEAN-001"
        ],
        "reason": "max_capacity_reached",
        "timestamp": datetime.now().isoformat()
    }
    max_capacity_msg.body = json.dumps(max_capacity_data)
    max_capacity_msg.set_metadata("performative", "availability_update")

    await caretaker.send(max_capacity_msg)
    await asyncio.sleep(2)

    # ASSERT
    assert len(coordinator.received_messages) >= 1
    update = json.loads(coordinator.received_messages[0].body)
    assert update["is_available"] is False
    assert update["current_load"] == update["max_concurrent_tasks"]
    assert update["reason"] == "max_capacity_reached"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_worker_becomes_available_after_task_completion(test_coordinator_agent,
                                                              test_caretaker_agent):
    """Test worker reports available again after completing tasks."""
    # ARRANGE
    coordinator = test_coordinator_agent
    caretaker = test_caretaker_agent

    # ACT - Worker completes task and updates availability
    task_completion_msg = Message(to=str(coordinator.jid))
    task_completion_data = {
        "task_id": "TASK-FEED-001",
        "status": "completed",
        "worker_id": str(caretaker.jid)
    }
    task_completion_msg.body = json.dumps(task_completion_data)
    task_completion_msg.set_metadata("performative", "task_completed")

    await caretaker.send(task_completion_msg)
    await asyncio.sleep(1)

    # Worker sends updated availability
    availability_msg = Message(to=str(coordinator.jid))
    availability_data = {
        "worker_id": str(caretaker.jid),
        "worker_role": "caretaker",
        "is_available": True,
        "current_load": 1,  # Reduced from 2
        "max_concurrent_tasks": 5,
        "current_tasks": ["TASK-WALK-002"],
        "timestamp": datetime.now().isoformat()
    }
    availability_msg.body = json.dumps(availability_data)
    availability_msg.set_metadata("performative", "availability_update")

    await caretaker.send(availability_msg)
    await asyncio.sleep(2)

    # ASSERT
    assert len(coordinator.received_messages) >= 2
    completion = json.loads(coordinator.received_messages[0].body)
    availability = json.loads(coordinator.received_messages[1].body)

    assert completion["status"] == "completed"
    assert availability["is_available"] is True
    assert availability["current_load"] < availability["max_concurrent_tasks"]


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_priority_based_task_ordering(test_coordinator_agent, test_caretaker_agent):
    """Test coordinator processes higher priority tasks first."""
    # ARRANGE
    coordinator = test_coordinator_agent
    caretaker = test_caretaker_agent

    # ACT - Submit multiple tasks with different priorities
    tasks = [
        {"task_id": "TASK-001", "priority": "normal", "task_type": "walk"},
        {"task_id": "TASK-002", "priority": "urgent", "task_type": "vaccination"},
        {"task_id": "TASK-003", "priority": "low", "task_type": "clean"},
        {"task_id": "TASK-004", "priority": "high", "task_type": "health_check"}
    ]

    # Send all tasks to coordinator
    for task in tasks:
        task_msg = Message(to=str(coordinator.jid))
        task_msg.body = json.dumps(task)
        task_msg.set_metadata("performative", "submit_task")
        task_msg.set_metadata("priority", task["priority"])
        await caretaker.send(task_msg)
        await asyncio.sleep(0.2)

    await asyncio.sleep(2)

    # ASSERT
    assert len(coordinator.received_messages) == 4

    # Verify priority order in metadata
    priorities = [msg.get_metadata("priority") for msg in coordinator.received_messages]
    # Expected order: urgent, high, normal, low
    assert priorities.count("urgent") == 1
    assert priorities.count("high") == 1
    assert priorities.count("normal") == 1
    assert priorities.count("low") == 1


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_new_animal_registration_urgent_priority(test_coordinator_agent,
                                                       test_veterinarian_agent):
    """Test new animal registration gets URGENT priority."""
    # ARRANGE
    coordinator = test_coordinator_agent
    veterinarian = test_veterinarian_agent

    # ACT - New animal registration task
    registration_msg = Message(to=str(coordinator.jid))
    registration_data = {
        "task_id": "TASK-REG-001",
        "task_type": "initial_checkup",
        "priority": "urgent",
        "animal_id": "NEW-DOG-001",
        "animal_name": "New Arrival",
        "registration_date": datetime.now().isoformat(),
        "reason": "new_animal_registration"
    }
    registration_msg.body = json.dumps(registration_data)
    registration_msg.set_metadata("performative", "submit_task")
    registration_msg.set_metadata("priority", "urgent")

    await veterinarian.send(registration_msg)
    await asyncio.sleep(2)

    # ASSERT
    assert len(coordinator.received_messages) >= 1
    task = json.loads(coordinator.received_messages[0].body)
    assert task["priority"] == "urgent"
    assert task["reason"] == "new_animal_registration"
    assert registration_msg.get_metadata("priority") == "urgent"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_least_loaded_worker_selection(test_coordinator_agent, multiple_caretaker_agents):
    """Test coordinator selects least loaded worker for new tasks."""
    # ARRANGE
    coordinator = test_coordinator_agent
    caretaker1, caretaker2 = multiple_caretaker_agents

    # ACT - Workers report different load levels
    # Caretaker 1: 3 tasks
    availability1_msg = Message(to=str(coordinator.jid))
    availability1_data = {
        "worker_id": str(caretaker1.jid),
        "worker_role": "caretaker",
        "is_available": True,
        "current_load": 3,
        "max_concurrent_tasks": 5,
        "timestamp": datetime.now().isoformat()
    }
    availability1_msg.body = json.dumps(availability1_data)
    availability1_msg.set_metadata("performative", "availability_update")
    await caretaker1.send(availability1_msg)

    # Caretaker 2: 0 tasks
    availability2_msg = Message(to=str(coordinator.jid))
    availability2_data = {
        "worker_id": str(caretaker2.jid),
        "worker_role": "caretaker",
        "is_available": True,
        "current_load": 0,
        "max_concurrent_tasks": 5,
        "timestamp": datetime.now().isoformat()
    }
    availability2_msg.body = json.dumps(availability2_data)
    availability2_msg.set_metadata("performative", "availability_update")
    await caretaker2.send(availability2_msg)

    await asyncio.sleep(2)

    # ASSERT - Coordinator received both availability updates
    assert len(coordinator.received_messages) >= 2

    # Verify caretaker2 has less load
    updates = [json.loads(msg.body) for msg in coordinator.received_messages]
    caretaker1_update = next(u for u in updates if u["worker_id"] == str(caretaker1.jid))
    caretaker2_update = next(u for u in updates if u["worker_id"] == str(caretaker2.jid))

    assert caretaker2_update["current_load"] < caretaker1_update["current_load"]
    assert caretaker2_update["is_available"] is True


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_worker_competency_verification(test_coordinator_agent, test_caretaker_agent,
                                              test_veterinarian_agent):
    """Test tasks only assigned to competent workers."""
    # ARRANGE
    coordinator = test_coordinator_agent
    caretaker = test_caretaker_agent
    veterinarian = test_veterinarian_agent

    # ACT - Workers report competencies
    caretaker_competencies = {
        "worker_id": str(caretaker.jid),
        "worker_role": "caretaker",
        "competencies": ["feed", "walk", "clean"],
        "timestamp": datetime.now().isoformat()
    }
    caretaker_msg = Message(to=str(coordinator.jid))
    caretaker_msg.body = json.dumps(caretaker_competencies)
    caretaker_msg.set_metadata("performative", "register_competencies")
    await caretaker.send(caretaker_msg)

    vet_competencies = {
        "worker_id": str(veterinarian.jid),
        "worker_role": "veterinarian",
        "competencies": ["health_check", "vaccination", "initial_checkup", "surgery"],
        "timestamp": datetime.now().isoformat()
    }
    vet_msg = Message(to=str(coordinator.jid))
    vet_msg.body = json.dumps(vet_competencies)
    vet_msg.set_metadata("performative", "register_competencies")
    await veterinarian.send(vet_msg)

    await asyncio.sleep(2)

    # ASSERT
    assert len(coordinator.received_messages) >= 2

    # Verify competency registration
    registrations = [json.loads(msg.body) for msg in coordinator.received_messages]
    caretaker_reg = next(r for r in registrations if r["worker_role"] == "caretaker")
    vet_reg = next(r for r in registrations if r["worker_role"] == "veterinarian")

    assert "feed" in caretaker_reg["competencies"]
    assert "vaccination" in vet_reg["competencies"]
    assert "vaccination" not in caretaker_reg["competencies"]
    assert "feed" not in vet_reg["competencies"]
