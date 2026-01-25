"""Unit tests for the Enums module."""

import pytest
from models.enums import (
    Priority, WorkerRole, TaskStatus, TaskType,
    AnimalHealthStatus, AnimalAdoptionStatus,
    RoomState, RoomType, ApplicationStatus
)


class TestPriorityEnum:
    """Test Priority enumeration."""

    def test_priority_urgent_value(self):
        """Test URGENT priority value."""
        assert Priority.URGENT.value == 1

    def test_priority_high_value(self):
        """Test HIGH priority value."""
        assert Priority.HIGH.value == 2

    def test_priority_normal_value(self):
        """Test NORMAL priority value."""
        assert Priority.NORMAL.value == 3

    def test_priority_low_value(self):
        """Test LOW priority value."""
        assert Priority.LOW.value == 4

    def test_all_priority_values_unique(self):
        """Test that all priority values are unique."""
        values = [p.value for p in Priority]
        assert len(values) == len(set(values))


class TestWorkerRoleEnum:
    """Test WorkerRole enumeration."""

    def test_coordinator_role(self):
        """Test COORDINATOR role value."""
        assert WorkerRole.COORDINATOR.value == "coordinator"

    def test_caretaker_role(self):
        """Test CARETAKER role value."""
        assert WorkerRole.CARETAKER.value == "caretaker"

    def test_cleaner_role(self):
        """Test CLEANER role value."""
        assert WorkerRole.CLEANER.value == "cleaner"

    def test_veterinarian_role(self):
        """Test VETERINARIAN role value."""
        assert WorkerRole.VETERINARIAN.value == "veterinarian"

    def test_reception_role(self):
        """Test RECEPTION role value."""
        assert WorkerRole.RECEPTION.value == "reception"

    def test_adoption_role(self):
        """Test ADOPTION role value."""
        assert WorkerRole.ADOPTION.value == "adoption"

    def test_worker_role_from_string(self):
        """Test creating WorkerRole from string value."""
        role = WorkerRole("caretaker")
        assert role == WorkerRole.CARETAKER


class TestTaskStatusEnum:
    """Test TaskStatus enumeration."""

    def test_pending_status(self):
        """Test PENDING status value."""
        assert TaskStatus.PENDING.value == "pending"

    def test_assigned_status(self):
        """Test ASSIGNED status value."""
        assert TaskStatus.ASSIGNED.value == "assigned"

    def test_in_progress_status(self):
        """Test IN_PROGRESS status value."""
        assert TaskStatus.IN_PROGRESS.value == "in_progress"

    def test_done_status(self):
        """Test DONE status value."""
        assert TaskStatus.DONE.value == "done"

    def test_failed_status(self):
        """Test FAILED status value."""
        assert TaskStatus.FAILED.value == "failed"

    def test_cancelled_status(self):
        """Test CANCELLED status value."""
        assert TaskStatus.CANCELLED.value == "cancelled"

    def test_task_status_from_string(self):
        """Test creating TaskStatus from string value."""
        status = TaskStatus("in_progress")
        assert status == TaskStatus.IN_PROGRESS


class TestTaskTypeEnum:
    """Test TaskType enumeration."""

    def test_feed_type(self):
        """Test FEED type value."""
        assert TaskType.FEED.value == "feed"

    def test_walk_type(self):
        """Test WALK type value."""
        assert TaskType.WALK.value == "walk"

    def test_clean_type(self):
        """Test CLEAN type value."""
        assert TaskType.CLEAN.value == "clean"

    def test_vaccination_type(self):
        """Test VACCINATION type value."""
        assert TaskType.VACCINATION.value == "vaccination"

    def test_health_check_type(self):
        """Test HEALTH_CHECK type value."""
        assert TaskType.HEALTH_CHECK.value == "health_check"

    def test_initial_checkup_type(self):
        """Test INITIAL_CHECKUP type value."""
        assert TaskType.INITIAL_CHECKUP.value == "initial_checkup"

    def test_adoption_application_type(self):
        """Test ADOPTION_APPLICATION type value."""
        assert TaskType.ADOPTION_APPLICATION.value == "adoption_application"

    def test_task_type_from_string(self):
        """Test creating TaskType from string value."""
        task_type = TaskType("vaccination")
        assert task_type == TaskType.VACCINATION


class TestAnimalHealthStatusEnum:
    """Test AnimalHealthStatus enumeration."""

    def test_healthy_status(self):
        """Test HEALTHY status value."""
        assert AnimalHealthStatus.HEALTHY.value == "healthy"

    def test_sick_status(self):
        """Test SICK status value."""
        assert AnimalHealthStatus.SICK.value == "sick"

    def test_chronic_condition_status(self):
        """Test CHRONIC_CONDITION status value."""
        assert AnimalHealthStatus.CHRONIC_CONDITION.value == "chronic_condition"

    def test_recovering_status(self):
        """Test RECOVERING status value."""
        assert AnimalHealthStatus.RECOVERING.value == "recovering"

    def test_needs_checkup_status(self):
        """Test NEEDS_CHECKUP status value."""
        assert AnimalHealthStatus.NEEDS_CHECKUP.value == "needs_checkup"

    def test_health_status_from_string(self):
        """Test creating AnimalHealthStatus from string value."""
        status = AnimalHealthStatus("sick")
        assert status == AnimalHealthStatus.SICK


class TestAnimalAdoptionStatusEnum:
    """Test AnimalAdoptionStatus enumeration."""

    def test_available_status(self):
        """Test AVAILABLE status value."""
        assert AnimalAdoptionStatus.AVAILABLE.value == "available"

    def test_pending_status(self):
        """Test PENDING status value."""
        assert AnimalAdoptionStatus.PENDING.value == "pending"

    def test_adopted_status(self):
        """Test ADOPTED status value."""
        assert AnimalAdoptionStatus.ADOPTED.value == "adopted"

    def test_not_available_status(self):
        """Test NOT_AVAILABLE status value."""
        assert AnimalAdoptionStatus.NOT_AVAILABLE.value == "not_available"

    def test_adoption_status_from_string(self):
        """Test creating AnimalAdoptionStatus from string value."""
        status = AnimalAdoptionStatus("adopted")
        assert status == AnimalAdoptionStatus.ADOPTED


class TestRoomStateEnum:
    """Test RoomState enumeration."""

    def test_clean_state(self):
        """Test CLEAN state value."""
        assert RoomState.CLEAN.value == "clean"

    def test_dirty_state(self):
        """Test DIRTY state value."""
        assert RoomState.DIRTY.value == "dirty"

    def test_cleaning_in_progress_state(self):
        """Test CLEANING_IN_PROGRESS state value."""
        assert RoomState.CLEANING_IN_PROGRESS.value == "cleaning_in_progress"

    def test_room_state_from_string(self):
        """Test creating RoomState from string value."""
        state = RoomState("dirty")
        assert state == RoomState.DIRTY


class TestRoomTypeEnum:
    """Test RoomType enumeration."""

    def test_animal_housing_type(self):
        """Test ANIMAL_HOUSING type value."""
        assert RoomType.ANIMAL_HOUSING.value == "animal_housing"

    def test_medical_type(self):
        """Test MEDICAL type value."""
        assert RoomType.MEDICAL.value == "medical"

    def test_quarantine_type(self):
        """Test QUARANTINE type value."""
        assert RoomType.QUARANTINE.value == "quarantine"

    def test_common_type(self):
        """Test COMMON type value."""
        assert RoomType.COMMON.value == "common"

    def test_room_type_from_string(self):
        """Test creating RoomType from string value."""
        room_type = RoomType("quarantine")
        assert room_type == RoomType.QUARANTINE


class TestApplicationStatusEnum:
    """Test ApplicationStatus enumeration."""

    def test_submitted_status(self):
        """Test SUBMITTED status value."""
        assert ApplicationStatus.SUBMITTED.value == "submitted"

    def test_under_review_status(self):
        """Test UNDER_REVIEW status value."""
        assert ApplicationStatus.UNDER_REVIEW.value == "under_review"

    def test_approved_status(self):
        """Test APPROVED status value."""
        assert ApplicationStatus.APPROVED.value == "approved"

    def test_rejected_status(self):
        """Test REJECTED status value."""
        assert ApplicationStatus.REJECTED.value == "rejected"

    def test_completed_status(self):
        """Test COMPLETED status value."""
        assert ApplicationStatus.COMPLETED.value == "completed"

    def test_application_status_from_string(self):
        """Test creating ApplicationStatus from string value."""
        status = ApplicationStatus("under_review")
        assert status == ApplicationStatus.UNDER_REVIEW


class TestEnumCompleteness:
    """Test that all enums are complete and accessible."""

    def test_all_priority_members(self):
        """Test that all Priority members are accessible."""
        assert len(list(Priority)) == 4

    def test_all_worker_role_members(self):
        """Test that all WorkerRole members are accessible."""
        assert len(list(WorkerRole)) == 6

    def test_all_task_status_members(self):
        """Test that all TaskStatus members are accessible."""
        assert len(list(TaskStatus)) == 6

    def test_all_task_type_members(self):
        """Test that all TaskType members are accessible."""
        assert len(list(TaskType)) == 7

    def test_all_health_status_members(self):
        """Test that all AnimalHealthStatus members are accessible."""
        assert len(list(AnimalHealthStatus)) == 5

    def test_all_adoption_status_members(self):
        """Test that all AnimalAdoptionStatus members are accessible."""
        assert len(list(AnimalAdoptionStatus)) == 4

    def test_all_room_state_members(self):
        """Test that all RoomState members are accessible."""
        assert len(list(RoomState)) == 3

    def test_all_room_type_members(self):
        """Test that all RoomType members are accessible."""
        assert len(list(RoomType)) == 4

    def test_all_application_status_members(self):
        """Test that all ApplicationStatus members are accessible."""
        assert len(list(ApplicationStatus)) == 5
