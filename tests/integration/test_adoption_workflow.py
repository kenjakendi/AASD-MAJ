"""Integration tests for adoption application workflows.

Tests the complete workflow:
Applicant → Coordinator → Adoption Agent → Animal
"""

import pytest
import asyncio
from datetime import datetime
from spade.message import Message
import json


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_complete_adoption_application_workflow(test_applicant_agent,
                                                      test_coordinator_agent,
                                                      test_adoption_agent,
                                                      sample_adoption_application_data):
    """Test complete adoption application submission and processing."""
    # ARRANGE
    applicant = test_applicant_agent
    coordinator = test_coordinator_agent
    adoption_agent = test_adoption_agent

    # ACT - Applicant submits application to coordinator
    app_msg = Message(to=str(coordinator.jid))
    app_msg.body = json.dumps(sample_adoption_application_data)
    app_msg.set_metadata("performative", "submit_adoption_application")
    app_msg.set_metadata("application_id", "APP-001")

    await applicant.send(app_msg)
    await asyncio.sleep(2)

    # Coordinator forwards to adoption agent
    forward_msg = Message(to=str(adoption_agent.jid))
    forward_data = sample_adoption_application_data.copy()
    forward_data["application_id"] = "APP-001"
    forward_data["submitted_at"] = datetime.now().isoformat()
    forward_msg.body = json.dumps(forward_data)
    forward_msg.set_metadata("performative", "review_adoption_application")

    await coordinator.send(forward_msg)
    await asyncio.sleep(2)

    # ASSERT
    assert len(coordinator.received_messages) >= 1, "Coordinator should receive application"
    assert len(adoption_agent.received_messages) >= 1, "Adoption agent should receive forwarded application"

    # Verify application data
    received_app = json.loads(adoption_agent.received_messages[0].body)
    assert received_app["applicant_name"] == "John Doe"
    assert received_app["animal_id"] == "DOG001"
    assert received_app["application_id"] == "APP-001"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_adoption_application_approval(test_adoption_agent, test_applicant_agent,
                                             sample_adoption_application_data):
    """Test adoption application approval workflow."""
    # ARRANGE
    adoption_agent = test_adoption_agent
    applicant = test_applicant_agent

    # ACT - Adoption agent approves application
    approval_msg = Message(to=str(applicant.jid))
    approval_data = {
        "application_id": "APP-001",
        "status": "approved",
        "approved_by": str(adoption_agent.jid),
        "approved_at": datetime.now().isoformat(),
        "animal_id": sample_adoption_application_data["animal_id"],
        "next_steps": [
            "Schedule meet-and-greet",
            "Complete paperwork",
            "Pay adoption fee"
        ]
    }
    approval_msg.body = json.dumps(approval_data)
    approval_msg.set_metadata("performative", "adoption_approved")

    await adoption_agent.send(approval_msg)
    await asyncio.sleep(2)

    # ASSERT
    assert len(applicant.received_messages) >= 1
    received = applicant.received_messages[0]
    assert received.get_metadata("performative") == "adoption_approved"
    result = json.loads(received.body)
    assert result["status"] == "approved"
    assert "next_steps" in result


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_adoption_application_rejection(test_adoption_agent, test_applicant_agent):
    """Test adoption application rejection workflow."""
    # ARRANGE
    adoption_agent = test_adoption_agent
    applicant = test_applicant_agent

    # ACT - Adoption agent rejects application (age criteria)
    rejection_msg = Message(to=str(applicant.jid))
    rejection_data = {
        "application_id": "APP-002",
        "status": "rejected",
        "rejected_by": str(adoption_agent.jid),
        "rejected_at": datetime.now().isoformat(),
        "reason": "Applicant age below minimum requirement (18 years)",
        "rejection_code": "AGE_REQUIREMENT_NOT_MET"
    }
    rejection_msg.body = json.dumps(rejection_data)
    rejection_msg.set_metadata("performative", "adoption_rejected")

    await adoption_agent.send(rejection_msg)
    await asyncio.sleep(2)

    # ASSERT
    assert len(applicant.received_messages) >= 1
    received = applicant.received_messages[0]
    assert received.get_metadata("performative") == "adoption_rejected"
    result = json.loads(received.body)
    assert result["status"] == "rejected"
    assert result["rejection_code"] == "AGE_REQUIREMENT_NOT_MET"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_adoption_completion_notification(test_adoption_agent, test_coordinator_agent,
                                                test_animal_agent):
    """Test adoption completion notifies all parties."""
    # ARRANGE
    adoption_agent = test_adoption_agent
    coordinator = test_coordinator_agent
    animal_agent = test_animal_agent

    # ACT - Adoption agent sends completion notifications
    completion_data = {
        "application_id": "APP-001",
        "status": "completed",
        "animal_id": "DOG001",
        "adopter_name": "John Doe",
        "completion_date": datetime.now().isoformat()
    }

    # Notify coordinator
    coord_msg = Message(to=str(coordinator.jid))
    coord_msg.body = json.dumps(completion_data)
    coord_msg.set_metadata("performative", "adoption_completed")
    await adoption_agent.send(coord_msg)

    # Notify animal agent
    animal_msg = Message(to=str(animal_agent.jid))
    animal_msg.body = json.dumps(completion_data)
    animal_msg.set_metadata("performative", "update_adoption_status")
    await adoption_agent.send(animal_msg)

    await asyncio.sleep(2)

    # ASSERT
    assert len(coordinator.received_messages) >= 1, "Coordinator should be notified"
    assert len(animal_agent.received_messages) >= 1, "Animal agent should be notified"

    # Verify coordinator notification
    coord_received = json.loads(coordinator.received_messages[0].body)
    assert coord_received["status"] == "completed"
    assert coord_received["animal_id"] == "DOG001"

    # Verify animal notification
    animal_received = json.loads(animal_agent.received_messages[0].body)
    assert animal_received["animal_id"] == "DOG001"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(30)
async def test_adoption_reference_check_workflow(test_adoption_agent, test_applicant_agent,
                                                 sample_adoption_application_data):
    """Test reference check request during adoption review."""
    # ARRANGE
    adoption_agent = test_adoption_agent
    applicant = test_applicant_agent

    # ACT - Adoption agent requests additional information
    ref_check_msg = Message(to=str(applicant.jid))
    ref_check_data = {
        "application_id": "APP-001",
        "status": "under_review",
        "required_action": "provide_reference_contacts",
        "references_to_verify": sample_adoption_application_data["references"],
        "deadline": (datetime.now() + timedelta(days=7)).isoformat()
    }
    ref_check_msg.body = json.dumps(ref_check_data)
    ref_check_msg.set_metadata("performative", "request_additional_info")

    await adoption_agent.send(ref_check_msg)
    await asyncio.sleep(2)

    # Applicant provides reference details
    ref_response_msg = Message(to=str(adoption_agent.jid))
    ref_response_data = {
        "application_id": "APP-001",
        "reference_details": [
            {"name": "Reference 1", "phone": "+1234567891", "relationship": "Veterinarian"},
            {"name": "Reference 2", "phone": "+1234567892", "relationship": "Friend"}
        ]
    }
    ref_response_msg.body = json.dumps(ref_response_data)
    ref_response_msg.set_metadata("performative", "additional_info_provided")

    await applicant.send(ref_response_msg)
    await asyncio.sleep(2)

    # ASSERT
    assert len(applicant.received_messages) >= 1, "Applicant should receive request"
    assert len(adoption_agent.received_messages) >= 1, "Adoption agent should receive response"

    # Verify request
    request = json.loads(applicant.received_messages[0].body)
    assert request["status"] == "under_review"
    assert request["required_action"] == "provide_reference_contacts"

    # Verify response
    response = json.loads(adoption_agent.received_messages[0].body)
    assert "reference_details" in response
    assert len(response["reference_details"]) == 2
