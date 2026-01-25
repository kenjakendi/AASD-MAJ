"""Integration tests for veterinary care workflows.

Tests the complete workflow:
Animal → Coordinator → Veterinarian → Health Status Update
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from spade.message import Message
import json


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_initial_checkup_workflow(test_coordinator_agent, test_veterinarian_agent,
                                       test_animal_agent, sample_initial_checkup_data):
    """Test initial checkup for new animal registration."""
    # ARRANGE
    coordinator = test_coordinator_agent
    veterinarian = test_veterinarian_agent
    animal_agent = test_animal_agent

    # ACT - Coordinator assigns initial checkup (URGENT priority)
    checkup_msg = Message(to=str(veterinarian.jid))
    checkup_data = sample_initial_checkup_data.copy()
    checkup_data["task_id"] = "TASK-CHECKUP-001"
    checkup_data["assigned_by"] = str(coordinator.jid)
    checkup_msg.body = json.dumps(checkup_data)
    checkup_msg.set_metadata("performative", "assign_initial_checkup")
    checkup_msg.set_metadata("priority", "urgent")

    await coordinator.send(checkup_msg)
    await asyncio.sleep(2)

    # Veterinarian completes checkup
    result_msg = Message(to=str(coordinator.jid))
    result_data = {
        "task_id": "TASK-CHECKUP-001",
        "animal_id": checkup_data["animal_id"],
        "status": "completed",
        "worker_id": str(veterinarian.jid),
        "completed_at": datetime.now().isoformat(),
        "health_assessment": {
            "overall_health": "healthy",
            "weight_kg": 25.5,
            "temperature_celsius": 38.5,
            "heart_rate_bpm": 120,
            "notes": "Animal is healthy and ready for adoption"
        },
        "vaccinations_needed": ["rabies", "distemper", "parvovirus"],
        "cleared_for_adoption": True
    }
    result_msg.body = json.dumps(result_data)
    result_msg.set_metadata("performative", "task_completed")

    await veterinarian.send(result_msg)
    await asyncio.sleep(2)

    # ASSERT
    assert len(veterinarian.received_messages) >= 1, "Veterinarian should receive checkup task"
    assert len(coordinator.received_messages) >= 1, "Coordinator should receive results"

    # Verify task assignment
    assignment = json.loads(veterinarian.received_messages[0].body)
    assert assignment["task_type"] == "initial_checkup"
    assert assignment["priority"] == "urgent"

    # Verify results
    results = json.loads(coordinator.received_messages[0].body)
    assert results["status"] == "completed"
    assert results["cleared_for_adoption"] is True
    assert len(results["vaccinations_needed"]) == 3


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_vaccination_task_cascade(test_coordinator_agent, test_veterinarian_agent,
                                       sample_vaccination_data):
    """Test vaccination tasks created from initial checkup results."""
    # ARRANGE
    coordinator = test_coordinator_agent
    veterinarian = test_veterinarian_agent

    # ACT - Coordinator creates vaccination task (HIGH priority)
    vacc_msg = Message(to=str(veterinarian.jid))
    vacc_data = sample_vaccination_data.copy()
    vacc_data["task_id"] = "TASK-VACC-001"
    vacc_data["assigned_by"] = str(coordinator.jid)
    vacc_data["vaccine_type"] = "rabies"
    vacc_msg.body = json.dumps(vacc_data)
    vacc_msg.set_metadata("performative", "assign_vaccination_task")
    vacc_msg.set_metadata("priority", "high")

    await coordinator.send(vacc_msg)
    await asyncio.sleep(2)

    # Veterinarian completes vaccination
    vacc_result_msg = Message(to=str(coordinator.jid))
    vacc_result_data = {
        "task_id": "TASK-VACC-001",
        "animal_id": vacc_data["animal_id"],
        "status": "completed",
        "worker_id": str(veterinarian.jid),
        "completed_at": datetime.now().isoformat(),
        "vaccination_record": {
            "vaccine_type": "rabies",
            "vaccine_batch": "RB-2024-001",
            "administered_at": datetime.now().isoformat(),
            "next_due_date": (datetime.now() + timedelta(days=365)).isoformat(),
            "side_effects": "none"
        }
    }
    vacc_result_msg.body = json.dumps(vacc_result_data)
    vacc_result_msg.set_metadata("performative", "vaccination_completed")

    await veterinarian.send(vacc_result_msg)
    await asyncio.sleep(2)

    # ASSERT
    assert len(veterinarian.received_messages) >= 1
    assert len(coordinator.received_messages) >= 1

    # Verify vaccination task
    vacc_task = json.loads(veterinarian.received_messages[0].body)
    assert vacc_task["task_type"] == "vaccination"
    assert vacc_task["parameters"]["vaccine_type"] == "rabies"

    # Verify vaccination completion
    vacc_result = json.loads(coordinator.received_messages[0].body)
    assert vacc_result["status"] == "completed"
    assert "vaccination_record" in vacc_result
    assert vacc_result["vaccination_record"]["vaccine_type"] == "rabies"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_health_check_status_update(test_coordinator_agent, test_veterinarian_agent,
                                         test_animal_agent, sample_health_check_data):
    """Test routine health check updates animal health status."""
    # ARRANGE
    coordinator = test_coordinator_agent
    veterinarian = test_veterinarian_agent
    animal_agent = test_animal_agent

    # ACT - Coordinator assigns health check
    health_check_msg = Message(to=str(veterinarian.jid))
    health_check_data = sample_health_check_data.copy()
    health_check_data["task_id"] = "TASK-HEALTH-001"
    health_check_msg.body = json.dumps(health_check_data)
    health_check_msg.set_metadata("performative", "assign_health_check")

    await coordinator.send(health_check_msg)
    await asyncio.sleep(2)

    # Veterinarian completes check and notifies animal agent
    health_result_msg = Message(to=str(animal_agent.jid))
    health_result_data = {
        "task_id": "TASK-HEALTH-001",
        "animal_id": health_check_data["animal_id"],
        "status": "completed",
        "completed_at": datetime.now().isoformat(),
        "health_status_update": {
            "new_health_status": "healthy",
            "findings": "No issues detected",
            "recommendations": ["Continue current diet", "Regular exercise"],
            "next_checkup_date": (datetime.now() + timedelta(days=90)).isoformat()
        }
    }
    health_result_msg.body = json.dumps(health_result_data)
    health_result_msg.set_metadata("performative", "update_health_status")

    await veterinarian.send(health_result_msg)
    await asyncio.sleep(2)

    # ASSERT
    assert len(veterinarian.received_messages) >= 1, "Veterinarian should receive health check task"
    assert len(animal_agent.received_messages) >= 1, "Animal agent should receive status update"

    # Verify health check task
    task = json.loads(veterinarian.received_messages[0].body)
    assert task["task_type"] == "health_check"
    assert task["animal_id"] == "CAT001"

    # Verify status update
    update = json.loads(animal_agent.received_messages[0].body)
    assert update["health_status_update"]["new_health_status"] == "healthy"
    assert "next_checkup_date" in update["health_status_update"]


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_sick_animal_urgent_care(test_coordinator_agent, test_veterinarian_agent,
                                       test_animal_agent):
    """Test urgent care request for sick animal."""
    # ARRANGE
    coordinator = test_coordinator_agent
    veterinarian = test_veterinarian_agent
    animal_agent = test_animal_agent

    # ACT - Animal requests urgent care
    urgent_care_msg = Message(to=str(coordinator.jid))
    urgent_care_data = {
        "animal_id": "DOG005",
        "request_type": "urgent_care",
        "priority": "urgent",
        "symptoms": ["vomiting", "lethargy", "loss_of_appetite"],
        "severity": "high",
        "requested_at": datetime.now().isoformat()
    }
    urgent_care_msg.body = json.dumps(urgent_care_data)
    urgent_care_msg.set_metadata("performative", "request_urgent_care")
    urgent_care_msg.set_metadata("priority", "urgent")

    await animal_agent.send(urgent_care_msg)
    await asyncio.sleep(2)

    # Coordinator immediately assigns to veterinarian
    urgent_assign_msg = Message(to=str(veterinarian.jid))
    urgent_assign_data = urgent_care_data.copy()
    urgent_assign_data["task_id"] = "TASK-URGENT-001"
    urgent_assign_data["task_type"] = "urgent_care"
    urgent_assign_msg.body = json.dumps(urgent_assign_data)
    urgent_assign_msg.set_metadata("performative", "assign_urgent_care")
    urgent_assign_msg.set_metadata("priority", "urgent")

    await coordinator.send(urgent_assign_msg)
    await asyncio.sleep(2)

    # ASSERT
    assert len(coordinator.received_messages) >= 1, "Coordinator should receive urgent request"
    assert len(veterinarian.received_messages) >= 1, "Veterinarian should receive urgent assignment"

    # Verify urgent request
    request = json.loads(coordinator.received_messages[0].body)
    assert request["request_type"] == "urgent_care"
    assert request["severity"] == "high"
    assert urgent_care_msg.get_metadata("priority") == "urgent"

    # Verify urgent assignment
    assignment = json.loads(veterinarian.received_messages[0].body)
    assert assignment["task_type"] == "urgent_care"
    assert len(assignment["symptoms"]) == 3
    assert urgent_assign_msg.get_metadata("priority") == "urgent"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_vaccination_schedule_tracking(test_coordinator_agent, test_veterinarian_agent):
    """Test vaccination schedule creation and tracking."""
    # ARRANGE
    coordinator = test_coordinator_agent
    veterinarian = test_veterinarian_agent

    # ACT - Veterinarian creates vaccination schedule after initial checkup
    schedule_msg = Message(to=str(coordinator.jid))
    schedule_data = {
        "animal_id": "DOG004",
        "schedule_type": "vaccination_schedule",
        "vaccinations": [
            {
                "vaccine_type": "rabies",
                "priority": "high",
                "due_date": (datetime.now() + timedelta(days=7)).isoformat()
            },
            {
                "vaccine_type": "distemper",
                "priority": "high",
                "due_date": (datetime.now() + timedelta(days=14)).isoformat()
            },
            {
                "vaccine_type": "parvovirus",
                "priority": "normal",
                "due_date": (datetime.now() + timedelta(days=21)).isoformat()
            }
        ],
        "created_by": str(veterinarian.jid),
        "created_at": datetime.now().isoformat()
    }
    schedule_msg.body = json.dumps(schedule_data)
    schedule_msg.set_metadata("performative", "vaccination_schedule_created")

    await veterinarian.send(schedule_msg)
    await asyncio.sleep(2)

    # ASSERT
    assert len(coordinator.received_messages) >= 1
    schedule = json.loads(coordinator.received_messages[0].body)
    assert schedule["schedule_type"] == "vaccination_schedule"
    assert len(schedule["vaccinations"]) == 3
    assert all("due_date" in v for v in schedule["vaccinations"])
