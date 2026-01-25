"""Unit tests for the AdoptionApplication model."""

import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time
from models.adoption_application import AdoptionApplication
from models.enums import ApplicationStatus


class TestAdoptionApplicationInitialization:
    """Test AdoptionApplication model initialization."""

    def test_application_creation_with_required_fields(self):
        """Test creating an application with only required fields."""
        app = AdoptionApplication(
            application_id="APP-001",
            applicant_id="APPL-001",
            animal_id="DOG001",
            applicant_name="John Doe",
            applicant_age=30,
            applicant_contact="john@email.com",
            applicant_address="123 Main St"
        )

        assert app.application_id == "APP-001"
        assert app.applicant_id == "APPL-001"
        assert app.animal_id == "DOG001"
        assert app.applicant_name == "John Doe"
        assert app.applicant_age == 30
        assert app.status == ApplicationStatus.SUBMITTED

    def test_application_creation_with_all_fields(self, sample_adoption_application):
        """Test creating an application with all fields."""
        assert sample_adoption_application.application_id == "APP001"
        assert sample_adoption_application.applicant_name == "Jane Doe"
        assert sample_adoption_application.status == ApplicationStatus.SUBMITTED
        assert sample_adoption_application.has_yard is True


class TestAdoptionApplicationSerialization:
    """Test AdoptionApplication serialization and deserialization."""

    def test_to_dict_produces_correct_structure(self, sample_adoption_application):
        """Test that to_dict() produces correct JSON structure."""
        data = sample_adoption_application.to_dict()

        assert data['application_id'] == "APP001"
        assert data['applicant_name'] == "Jane Doe"
        assert data['applicant_age'] == 30
        assert data['animal_id'] == "DOG001"
        assert data['status'] == "submitted"
        assert 'submitted_at' in data

    def test_from_dict_restores_object_correctly(self, sample_adoption_application):
        """Test that from_dict() restores object correctly."""
        data = sample_adoption_application.to_dict()
        restored = AdoptionApplication.from_dict(data)

        assert restored.application_id == sample_adoption_application.application_id
        assert restored.applicant_name == sample_adoption_application.applicant_name
        assert restored.applicant_age == sample_adoption_application.applicant_age
        assert restored.status == sample_adoption_application.status

    def test_roundtrip_serialization_maintains_integrity(self, approved_adoption_application):
        """Test that roundtrip serialization maintains data integrity."""
        data = approved_adoption_application.to_dict()
        restored = AdoptionApplication.from_dict(data)
        data2 = restored.to_dict()

        assert data['application_id'] == data2['application_id']
        assert data['status'] == data2['status']
        assert data['applicant_name'] == data2['applicant_name']

    def test_serialization_with_datetime_fields(self):
        """Test serialization with datetime fields."""
        app = AdoptionApplication(
            application_id="APP-002",
            applicant_id="APPL-002",
            animal_id="CAT001",
            applicant_name="Test User",
            applicant_age=25,
            applicant_contact="test@email.com",
            applicant_address="456 Oak Ave",
            submitted_at=datetime(2024, 1, 15, 10, 0, 0),
            reviewed_at=datetime(2024, 1, 16, 14, 0, 0)
        )

        data = app.to_dict()
        assert data['submitted_at'] == "2024-01-15T10:00:00"
        assert data['reviewed_at'] == "2024-01-16T14:00:00"


class TestAdoptionApplicationApprove:
    """Test approve() method."""

    @freeze_time("2024-01-16 10:00:00")
    def test_approve_changes_status(self, sample_adoption_application):
        """Test that approve() changes status to APPROVED."""
        sample_adoption_application.approve()

        assert sample_adoption_application.status == ApplicationStatus.APPROVED

    @freeze_time("2024-01-16 10:00:00")
    def test_approve_sets_reviewed_at_timestamp(self, sample_adoption_application):
        """Test that approve() sets reviewed_at timestamp."""
        sample_adoption_application.approve()

        assert sample_adoption_application.reviewed_at == datetime(2024, 1, 16, 10, 0, 0)

    def test_approve_stores_notes(self, sample_adoption_application):
        """Test that approve() stores reviewer notes."""
        notes = "Excellent references, suitable home environment"
        sample_adoption_application.approve(notes=notes)

        assert sample_adoption_application.reviewer_notes == notes
        assert sample_adoption_application.status == ApplicationStatus.APPROVED

    def test_approve_with_empty_notes(self, sample_adoption_application):
        """Test that approve() works with empty notes."""
        sample_adoption_application.approve(notes="")

        assert sample_adoption_application.reviewer_notes == ""
        assert sample_adoption_application.status == ApplicationStatus.APPROVED


class TestAdoptionApplicationReject:
    """Test reject() method."""

    @freeze_time("2024-01-16 11:00:00")
    def test_reject_changes_status(self, sample_adoption_application):
        """Test that reject() changes status to REJECTED."""
        sample_adoption_application.reject("Insufficient experience")

        assert sample_adoption_application.status == ApplicationStatus.REJECTED

    @freeze_time("2024-01-16 11:00:00")
    def test_reject_sets_reviewed_at_timestamp(self, sample_adoption_application):
        """Test that reject() sets reviewed_at timestamp."""
        sample_adoption_application.reject("No yard for large dog")

        assert sample_adoption_application.reviewed_at == datetime(2024, 1, 16, 11, 0, 0)

    def test_reject_stores_reason(self, sample_adoption_application):
        """Test that reject() stores rejection reason."""
        reason = "Living situation not suitable for this animal"
        sample_adoption_application.reject(reason)

        assert sample_adoption_application.rejection_reason == reason
        assert sample_adoption_application.status == ApplicationStatus.REJECTED


class TestAdoptionApplicationComplete:
    """Test complete() method."""

    @freeze_time("2024-01-17 14:00:00")
    def test_complete_changes_status(self, approved_adoption_application):
        """Test that complete() changes status to COMPLETED."""
        approved_adoption_application.complete()

        assert approved_adoption_application.status == ApplicationStatus.COMPLETED

    @freeze_time("2024-01-17 14:00:00")
    def test_complete_sets_completed_at_timestamp(self, approved_adoption_application):
        """Test that complete() sets completed_at timestamp."""
        approved_adoption_application.complete()

        assert approved_adoption_application.completed_at == datetime(2024, 1, 17, 14, 0, 0)


class TestAdoptionApplicationStartReview:
    """Test start_review() method."""

    @freeze_time("2024-01-16 09:00:00")
    def test_start_review_changes_status(self, sample_adoption_application):
        """Test that start_review() changes status to UNDER_REVIEW."""
        sample_adoption_application.start_review()

        assert sample_adoption_application.status == ApplicationStatus.UNDER_REVIEW

    @freeze_time("2024-01-16 09:00:00")
    def test_start_review_sets_reviewed_at_timestamp(self, sample_adoption_application):
        """Test that start_review() sets reviewed_at timestamp."""
        sample_adoption_application.start_review()

        assert sample_adoption_application.reviewed_at == datetime(2024, 1, 16, 9, 0, 0)


class TestAdoptionApplicationWorkflow:
    """Test complete adoption application workflow."""

    @freeze_time("2024-01-15 10:00:00")
    def test_complete_workflow_approval(self):
        """Test complete workflow from submission to completion (approval path)."""
        app = AdoptionApplication(
            application_id="APP-WF1",
            applicant_id="APPL-WF1",
            animal_id="DOG001",
            applicant_name="Workflow Test",
            applicant_age=35,
            applicant_contact="workflow@email.com",
            applicant_address="789 Pine St"
        )

        # Initial state
        assert app.status == ApplicationStatus.SUBMITTED

        # Start review
        with freeze_time("2024-01-16 09:00:00"):
            app.start_review()
            assert app.status == ApplicationStatus.UNDER_REVIEW
            assert app.reviewed_at == datetime(2024, 1, 16, 9, 0, 0)

        # Approve
        with freeze_time("2024-01-16 14:00:00"):
            app.approve("Good candidate")
            assert app.status == ApplicationStatus.APPROVED
            assert app.reviewer_notes == "Good candidate"

        # Complete
        with freeze_time("2024-01-17 10:00:00"):
            app.complete()
            assert app.status == ApplicationStatus.COMPLETED
            assert app.completed_at == datetime(2024, 1, 17, 10, 0, 0)

    @freeze_time("2024-01-15 10:00:00")
    def test_complete_workflow_rejection(self):
        """Test complete workflow with rejection path."""
        app = AdoptionApplication(
            application_id="APP-WF2",
            applicant_id="APPL-WF2",
            animal_id="CAT001",
            applicant_name="Rejected Test",
            applicant_age=20,
            applicant_contact="rejected@email.com",
            applicant_address="100 Elm St"
        )

        # Start review
        with freeze_time("2024-01-16 09:00:00"):
            app.start_review()
            assert app.status == ApplicationStatus.UNDER_REVIEW

        # Reject
        with freeze_time("2024-01-16 11:00:00"):
            app.reject("No previous pet experience")
            assert app.status == ApplicationStatus.REJECTED
            assert app.rejection_reason == "No previous pet experience"


class TestAdoptionApplicationEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_application_with_minimum_age(self):
        """Test application with minimum valid age."""
        app = AdoptionApplication(
            application_id="APP-003",
            applicant_id="APPL-003",
            animal_id="DOG002",
            applicant_name="Young Applicant",
            applicant_age=18,
            applicant_contact="young@email.com",
            applicant_address="200 Maple St"
        )

        assert app.applicant_age == 18

    def test_application_with_no_previous_experience(self):
        """Test application with no previous pet experience."""
        app = AdoptionApplication(
            application_id="APP-004",
            applicant_id="APPL-004",
            animal_id="CAT002",
            applicant_name="No Experience",
            applicant_age=25,
            applicant_contact="noexp@email.com",
            applicant_address="300 Birch St",
            has_previous_pet_experience=False
        )

        assert app.has_previous_pet_experience is False

    def test_application_with_other_pets(self):
        """Test application with other pets in household."""
        app = AdoptionApplication(
            application_id="APP-005",
            applicant_id="APPL-005",
            animal_id="DOG003",
            applicant_name="Multi Pet",
            applicant_age=40,
            applicant_contact="multipet@email.com",
            applicant_address="400 Cedar St",
            other_pets=["cat", "hamster"]
        )

        assert len(app.other_pets) == 2
        assert "cat" in app.other_pets

    def test_application_with_references(self):
        """Test application with references."""
        app = AdoptionApplication(
            application_id="APP-006",
            applicant_id="APPL-006",
            animal_id="CAT003",
            applicant_name="With References",
            applicant_age=32,
            applicant_contact="refs@email.com",
            applicant_address="500 Spruce St",
            references=["Veterinarian: Dr. Smith", "Friend: Jane Doe"]
        )

        assert len(app.references) == 2

    def test_application_with_large_household(self):
        """Test application with large household."""
        app = AdoptionApplication(
            application_id="APP-007",
            applicant_id="APPL-007",
            animal_id="DOG004",
            applicant_name="Big Family",
            applicant_age=45,
            applicant_contact="family@email.com",
            applicant_address="600 Willow St",
            household_members=6
        )

        assert app.household_members == 6

    def test_application_employment_status(self):
        """Test application with employment status."""
        app = AdoptionApplication(
            application_id="APP-008",
            applicant_id="APPL-008",
            animal_id="CAT004",
            applicant_name="Employed",
            applicant_age=30,
            applicant_contact="employed@email.com",
            applicant_address="700 Ash St",
            employment_status="Full-time"
        )

        assert app.employment_status == "Full-time"

    def test_application_apartment_without_yard(self):
        """Test application for apartment without yard."""
        app = AdoptionApplication(
            application_id="APP-009",
            applicant_id="APPL-009",
            animal_id="CAT005",
            applicant_name="Apartment Dweller",
            applicant_age=28,
            applicant_contact="apt@email.com",
            applicant_address="800 Poplar St",
            home_type="apartment",
            has_yard=False
        )

        assert app.home_type == "apartment"
        assert app.has_yard is False
