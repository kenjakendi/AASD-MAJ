"""Unit tests for the Task model."""

import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time
from models.task import Task
from models.enums import TaskStatus, TaskType, Priority


class TestTaskInitialization:
    """Test Task model initialization."""

    def test_task_creation_with_required_fields(self):
        """Test creating a task with only required fields."""
        task = Task(
            task_id="TASK-001",
            task_type=TaskType.FEED,
            priority=Priority.NORMAL
        )

        assert task.task_id == "TASK-001"
        assert task.task_type == TaskType.FEED
        assert task.priority == Priority.NORMAL
        assert task.status == TaskStatus.PENDING
        assert task.attempts == 0
        assert task.max_attempts == 3

    def test_task_creation_with_all_fields(self, sample_feed_task):
        """Test creating a task with all fields."""
        assert sample_feed_task.task_id == "FEED-001"
        assert sample_feed_task.task_type == TaskType.FEED
        assert sample_feed_task.priority == Priority.NORMAL
        assert sample_feed_task.status == TaskStatus.PENDING
        assert isinstance(sample_feed_task.parameters, dict)


class TestTaskSerialization:
    """Test Task serialization and deserialization."""

    def test_to_dict_produces_correct_structure(self, sample_feed_task):
        """Test that to_dict() produces correct JSON structure."""
        data = sample_feed_task.to_dict()

        assert data['task_id'] == "FEED-001"
        assert data['task_type'] == "feed"
        assert data['priority'] == 3
        assert data['status'] == "pending"
        assert 'parameters' in data
        assert 'created_at' in data
        assert 'attempts' in data

    def test_from_dict_restores_object_correctly(self, sample_feed_task):
        """Test that from_dict() restores object correctly."""
        data = sample_feed_task.to_dict()
        restored = Task.from_dict(data)

        assert restored.task_id == sample_feed_task.task_id
        assert restored.task_type == sample_feed_task.task_type
        assert restored.priority == sample_feed_task.priority
        assert restored.status == sample_feed_task.status
        assert restored.parameters == sample_feed_task.parameters

    def test_roundtrip_serialization_maintains_integrity(self, sample_feed_task):
        """Test that roundtrip serialization maintains data integrity."""
        data = sample_feed_task.to_dict()
        restored = Task.from_dict(data)
        data2 = restored.to_dict()

        # Compare all serializable fields
        assert data['task_id'] == data2['task_id']
        assert data['task_type'] == data2['task_type']
        assert data['priority'] == data2['priority']
        assert data['status'] == data2['status']

    def test_serialization_with_datetime_fields(self):
        """Test serialization with various datetime fields."""
        task = Task(
            task_id="TASK-002",
            task_type=TaskType.WALK,
            priority=Priority.HIGH,
            created_at=datetime(2024, 1, 15, 10, 0, 0),
            assigned_at=datetime(2024, 1, 15, 10, 5, 0),
            started_at=datetime(2024, 1, 15, 10, 10, 0)
        )

        data = task.to_dict()
        assert data['created_at'] == "2024-01-15T10:00:00"
        assert data['assigned_at'] == "2024-01-15T10:05:00"
        assert data['started_at'] == "2024-01-15T10:10:00"

    def test_deserialization_with_datetime_strings(self):
        """Test deserializing tasks with datetime strings."""
        data = {
            'task_id': 'TASK-003',
            'task_type': 'clean',
            'priority': 2,
            'status': 'done',
            'created_at': '2024-01-15T08:00:00',
            'assigned_at': '2024-01-15T08:05:00',
            'started_at': '2024-01-15T08:10:00',
            'completed_at': '2024-01-15T08:30:00'
        }

        task = Task.from_dict(data)
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.assigned_at, datetime)
        assert isinstance(task.started_at, datetime)
        assert isinstance(task.completed_at, datetime)


class TestTaskCanRetry:
    """Test can_retry() method."""

    def test_can_retry_when_no_attempts(self):
        """Test that task can retry when no attempts made."""
        task = Task(
            task_id="TASK-004",
            task_type=TaskType.FEED,
            priority=Priority.NORMAL
        )

        assert task.can_retry() is True

    def test_can_retry_when_below_max_attempts(self):
        """Test that task can retry when attempts below max."""
        task = Task(
            task_id="TASK-005",
            task_type=TaskType.WALK,
            priority=Priority.NORMAL,
            attempts=2,
            max_attempts=3
        )

        assert task.can_retry() is True

    def test_cannot_retry_when_max_attempts_reached(self):
        """Test that task cannot retry when max attempts reached."""
        task = Task(
            task_id="TASK-006",
            task_type=TaskType.CLEAN,
            priority=Priority.LOW,
            attempts=3,
            max_attempts=3
        )

        assert task.can_retry() is False

    def test_cannot_retry_when_max_attempts_exceeded(self):
        """Test that task cannot retry when max attempts exceeded."""
        task = Task(
            task_id="TASK-007",
            task_type=TaskType.VACCINATION,
            priority=Priority.URGENT,
            attempts=4,
            max_attempts=3
        )

        assert task.can_retry() is False


class TestTaskIsOverdue:
    """Test is_overdue() method."""

    @freeze_time("2024-01-15 12:00:00")
    def test_is_overdue_when_timeout_exceeded(self):
        """Test that task is overdue when timeout exceeded."""
        task = Task(
            task_id="TASK-008",
            task_type=TaskType.FEED,
            priority=Priority.NORMAL,
            started_at=datetime(2024, 1, 15, 11, 50, 0)  # 10 minutes ago
        )

        assert task.is_overdue(timeout_seconds=300) is True  # 5 minute timeout

    @freeze_time("2024-01-15 12:00:00")
    def test_not_overdue_when_within_timeout(self):
        """Test that task is not overdue when within timeout."""
        task = Task(
            task_id="TASK-009",
            task_type=TaskType.WALK,
            priority=Priority.HIGH,
            started_at=datetime(2024, 1, 15, 11, 57, 0)  # 3 minutes ago
        )

        assert task.is_overdue(timeout_seconds=300) is False  # 5 minute timeout

    def test_not_overdue_when_not_started(self):
        """Test that task is not overdue when not started."""
        task = Task(
            task_id="TASK-010",
            task_type=TaskType.CLEAN,
            priority=Priority.NORMAL
        )

        assert task.is_overdue(timeout_seconds=300) is False

    @freeze_time("2024-01-15 12:00:00")
    def test_not_overdue_when_completed(self):
        """Test that task is not overdue when completed."""
        task = Task(
            task_id="TASK-011",
            task_type=TaskType.HEALTH_CHECK,
            priority=Priority.HIGH,
            started_at=datetime(2024, 1, 15, 11, 30, 0),
            completed_at=datetime(2024, 1, 15, 11, 45, 0)
        )

        assert task.is_overdue(timeout_seconds=300) is False


class TestTaskAssign:
    """Test assign() method."""

    @freeze_time("2024-01-15 10:00:00")
    def test_assign_updates_worker_id(self):
        """Test that assign() sets the worker ID."""
        task = Task(
            task_id="TASK-012",
            task_type=TaskType.FEED,
            priority=Priority.NORMAL
        )

        task.assign("WORKER-001")
        assert task.assigned_to == "WORKER-001"

    @freeze_time("2024-01-15 10:00:00")
    def test_assign_sets_assigned_at_timestamp(self):
        """Test that assign() sets the assigned_at timestamp."""
        task = Task(
            task_id="TASK-013",
            task_type=TaskType.WALK,
            priority=Priority.HIGH
        )

        task.assign("WORKER-002")
        assert task.assigned_at == datetime(2024, 1, 15, 10, 0, 0)

    def test_assign_changes_status_to_assigned(self):
        """Test that assign() changes status to ASSIGNED."""
        task = Task(
            task_id="TASK-014",
            task_type=TaskType.CLEAN,
            priority=Priority.NORMAL,
            status=TaskStatus.PENDING
        )

        task.assign("WORKER-003")
        assert task.status == TaskStatus.ASSIGNED

    def test_assign_increments_attempts(self):
        """Test that assign() increments attempt counter."""
        task = Task(
            task_id="TASK-015",
            task_type=TaskType.VACCINATION,
            priority=Priority.URGENT,
            attempts=0
        )

        task.assign("WORKER-004")
        assert task.attempts == 1

        task.assign("WORKER-005")
        assert task.attempts == 2


class TestTaskStart:
    """Test start() method."""

    @freeze_time("2024-01-15 11:30:00")
    def test_start_sets_started_at_timestamp(self):
        """Test that start() sets the started_at timestamp."""
        task = Task(
            task_id="TASK-016",
            task_type=TaskType.FEED,
            priority=Priority.NORMAL
        )

        task.start()
        assert task.started_at == datetime(2024, 1, 15, 11, 30, 0)

    def test_start_changes_status_to_in_progress(self):
        """Test that start() changes status to IN_PROGRESS."""
        task = Task(
            task_id="TASK-017",
            task_type=TaskType.WALK,
            priority=Priority.HIGH,
            status=TaskStatus.ASSIGNED
        )

        task.start()
        assert task.status == TaskStatus.IN_PROGRESS


class TestTaskComplete:
    """Test complete() method."""

    @freeze_time("2024-01-15 12:00:00")
    def test_complete_sets_completed_at_timestamp(self):
        """Test that complete() sets the completed_at timestamp."""
        task = Task(
            task_id="TASK-018",
            task_type=TaskType.FEED,
            priority=Priority.NORMAL,
            status=TaskStatus.IN_PROGRESS
        )

        result = {"status": "success", "message": "Task completed"}
        task.complete(result)
        assert task.completed_at == datetime(2024, 1, 15, 12, 0, 0)

    def test_complete_changes_status_to_done(self):
        """Test that complete() changes status to DONE."""
        task = Task(
            task_id="TASK-019",
            task_type=TaskType.WALK,
            priority=Priority.HIGH,
            status=TaskStatus.IN_PROGRESS
        )

        result = {"distance": "2km", "duration": "30min"}
        task.complete(result)
        assert task.status == TaskStatus.DONE

    def test_complete_stores_result(self):
        """Test that complete() stores the result."""
        task = Task(
            task_id="TASK-020",
            task_type=TaskType.HEALTH_CHECK,
            priority=Priority.URGENT,
            status=TaskStatus.IN_PROGRESS
        )

        result = {"health_status": "healthy", "temperature": "38.5C"}
        task.complete(result)
        assert task.result == result


class TestTaskFail:
    """Test fail() method."""

    @freeze_time("2024-01-15 12:30:00")
    def test_fail_sets_completed_at_timestamp(self):
        """Test that fail() sets the completed_at timestamp."""
        task = Task(
            task_id="TASK-021",
            task_type=TaskType.FEED,
            priority=Priority.NORMAL,
            status=TaskStatus.IN_PROGRESS
        )

        task.fail("Animal not found")
        assert task.completed_at == datetime(2024, 1, 15, 12, 30, 0)

    def test_fail_changes_status_to_failed(self):
        """Test that fail() changes status to FAILED."""
        task = Task(
            task_id="TASK-022",
            task_type=TaskType.WALK,
            priority=Priority.HIGH,
            status=TaskStatus.IN_PROGRESS
        )

        task.fail("Weather conditions unsuitable")
        assert task.status == TaskStatus.FAILED

    def test_fail_stores_error_message(self):
        """Test that fail() stores the error message."""
        task = Task(
            task_id="TASK-023",
            task_type=TaskType.VACCINATION,
            priority=Priority.URGENT,
            status=TaskStatus.IN_PROGRESS
        )

        error_msg = "Vaccine stock depleted"
        task.fail(error_msg)
        assert task.error_message == error_msg


class TestTaskLifecycle:
    """Test complete task lifecycle."""

    @freeze_time("2024-01-15 10:00:00")
    def test_complete_task_lifecycle_success(self):
        """Test full task lifecycle from PENDING to DONE."""
        task = Task(
            task_id="TASK-024",
            task_type=TaskType.FEED,
            priority=Priority.NORMAL
        )

        # Initial state
        assert task.status == TaskStatus.PENDING
        assert task.attempts == 0

        # Assign task
        with freeze_time("2024-01-15 10:00:00"):
            task.assign("WORKER-001")
            assert task.status == TaskStatus.ASSIGNED
            assert task.assigned_to == "WORKER-001"
            assert task.attempts == 1

        # Start task
        with freeze_time("2024-01-15 10:05:00"):
            task.start()
            assert task.status == TaskStatus.IN_PROGRESS
            assert task.started_at == datetime(2024, 1, 15, 10, 5, 0)

        # Complete task
        with freeze_time("2024-01-15 10:15:00"):
            result = {"status": "fed", "food_amount": "200g"}
            task.complete(result)
            assert task.status == TaskStatus.DONE
            assert task.completed_at == datetime(2024, 1, 15, 10, 15, 0)
            assert task.result == result

    @freeze_time("2024-01-15 10:00:00")
    def test_task_lifecycle_with_failure(self):
        """Test task lifecycle with failure."""
        task = Task(
            task_id="TASK-025",
            task_type=TaskType.WALK,
            priority=Priority.HIGH
        )

        # Assign and start
        with freeze_time("2024-01-15 10:00:00"):
            task.assign("WORKER-002")
            task.start()

        # Fail task
        with freeze_time("2024-01-15 10:10:00"):
            task.fail("Animal refused to walk")
            assert task.status == TaskStatus.FAILED
            assert task.completed_at == datetime(2024, 1, 15, 10, 10, 0)
            assert task.error_message == "Animal refused to walk"


class TestTaskEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_task_with_empty_parameters(self):
        """Test task with empty parameters."""
        task = Task(
            task_id="TASK-026",
            task_type=TaskType.CLEAN,
            priority=Priority.LOW,
            parameters={}
        )

        assert task.parameters == {}

    def test_task_with_complex_parameters(self):
        """Test task with complex nested parameters."""
        complex_params = {
            "animal_id": "DOG001",
            "vaccinations": ["rabies", "distemper"],
            "schedule": {
                "date": "2024-01-15",
                "time": "10:00"
            }
        }

        task = Task(
            task_id="TASK-027",
            task_type=TaskType.VACCINATION,
            priority=Priority.URGENT,
            parameters=complex_params
        )

        data = task.to_dict()
        restored = Task.from_dict(data)
        assert restored.parameters == complex_params

    def test_task_with_urgent_priority(self):
        """Test task with URGENT priority."""
        task = Task(
            task_id="TASK-028",
            task_type=TaskType.HEALTH_CHECK,
            priority=Priority.URGENT
        )

        assert task.priority == Priority.URGENT
        assert task.to_dict()['priority'] == 1

    def test_task_with_low_priority(self):
        """Test task with LOW priority."""
        task = Task(
            task_id="TASK-029",
            task_type=TaskType.CLEAN,
            priority=Priority.LOW
        )

        assert task.priority == Priority.LOW
        assert task.to_dict()['priority'] == 4

    def test_task_max_attempts_customization(self):
        """Test task with custom max_attempts."""
        task = Task(
            task_id="TASK-030",
            task_type=TaskType.ADOPTION_APPLICATION,
            priority=Priority.NORMAL,
            max_attempts=5
        )

        assert task.max_attempts == 5
        assert task.can_retry() is True

        task.attempts = 5
        assert task.can_retry() is False
