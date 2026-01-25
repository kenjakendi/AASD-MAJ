"""Unit tests for the Worker model."""

import pytest
from models.worker import Worker, WorkerAvailability
from models.enums import WorkerRole, TaskType


class TestWorkerInitialization:
    """Test Worker model initialization."""

    def test_worker_creation_with_required_fields(self):
        """Test creating a worker with only required fields."""
        worker = Worker(
            worker_id="W001",
            name="Test Worker",
            role=WorkerRole.CARETAKER
        )

        assert worker.worker_id == "W001"
        assert worker.name == "Test Worker"
        assert worker.role == WorkerRole.CARETAKER
        assert worker.tasks_completed == 0
        assert worker.tasks_failed == 0

    def test_worker_creates_availability_by_default(self):
        """Test that worker creates WorkerAvailability by default."""
        worker = Worker(
            worker_id="W002",
            name="Auto Avail",
            role=WorkerRole.VETERINARIAN
        )

        assert worker.availability is not None
        assert worker.availability.worker_id == "W002"

    def test_worker_with_competencies(self, sample_caretaker):
        """Test worker with competencies."""
        assert TaskType.FEED.value in sample_caretaker.competencies
        assert TaskType.WALK.value in sample_caretaker.competencies


class TestWorkerSerialization:
    """Test Worker serialization and deserialization."""

    def test_to_dict_produces_correct_structure(self, sample_caretaker):
        """Test that to_dict() produces correct JSON structure."""
        data = sample_caretaker.to_dict()

        assert data['worker_id'] == "CARE001"
        assert data['name'] == "John Smith"
        assert data['role'] == "caretaker"
        assert 'competencies' in data
        assert 'availability' in data
        assert isinstance(data['competencies'], list)

    def test_from_dict_restores_object_correctly(self, sample_caretaker):
        """Test that from_dict() restores object correctly."""
        data = sample_caretaker.to_dict()
        restored = Worker.from_dict(data)

        assert restored.worker_id == sample_caretaker.worker_id
        assert restored.name == sample_caretaker.name
        assert restored.role == sample_caretaker.role
        assert restored.competencies == sample_caretaker.competencies

    def test_roundtrip_serialization_maintains_integrity(self, sample_veterinarian):
        """Test that roundtrip serialization maintains data integrity."""
        data = sample_veterinarian.to_dict()
        restored = Worker.from_dict(data)
        data2 = restored.to_dict()

        assert data['worker_id'] == data2['worker_id']
        assert data['role'] == data2['role']
        assert set(data['competencies']) == set(data2['competencies'])

    def test_serialization_with_availability(self):
        """Test serialization with WorkerAvailability."""
        worker = Worker(
            worker_id="W003",
            name="Available Worker",
            role=WorkerRole.CLEANER,
            competencies={TaskType.CLEAN.value}
        )

        worker.availability.is_available = True
        worker.availability.current_load = 2

        data = worker.to_dict()
        assert data['availability']['is_available'] is True
        assert data['availability']['current_load'] == 2

    def test_deserialization_with_availability(self):
        """Test deserializing worker with availability data."""
        data = {
            'worker_id': 'W004',
            'name': 'Test Worker',
            'role': 'veterinarian',
            'competencies': ['health_check', 'vaccination'],
            'max_concurrent_tasks': 2,
            'availability': {
                'worker_id': 'W004',
                'schedule': {},
                'is_available': False,
                'current_load': 2,
                'max_concurrent_tasks': 2
            }
        }

        worker = Worker.from_dict(data)
        assert worker.availability.is_available is False
        assert worker.availability.current_load == 2


class TestWorkerCanHandleTask:
    """Test can_handle_task() method."""

    def test_can_handle_task_in_competencies(self, sample_caretaker):
        """Test that worker can handle task in competencies."""
        assert sample_caretaker.can_handle_task(TaskType.FEED.value) is True
        assert sample_caretaker.can_handle_task(TaskType.WALK.value) is True

    def test_cannot_handle_task_not_in_competencies(self, sample_caretaker):
        """Test that worker cannot handle task not in competencies."""
        assert sample_caretaker.can_handle_task(TaskType.VACCINATION.value) is False
        assert sample_caretaker.can_handle_task(TaskType.HEALTH_CHECK.value) is False

    def test_veterinarian_can_handle_medical_tasks(self, sample_veterinarian):
        """Test that veterinarian can handle medical tasks."""
        assert sample_veterinarian.can_handle_task(TaskType.HEALTH_CHECK.value) is True
        assert sample_veterinarian.can_handle_task(TaskType.VACCINATION.value) is True

    def test_cleaner_can_handle_clean_tasks(self, sample_cleaner):
        """Test that cleaner can handle cleaning tasks."""
        assert sample_cleaner.can_handle_task(TaskType.CLEAN.value) is True
        assert sample_cleaner.can_handle_task(TaskType.FEED.value) is False


class TestWorkerIsAvailableForTask:
    """Test is_available_for_task() method."""

    def test_available_when_load_below_max(self, sample_caretaker):
        """Test that worker is available when load below max."""
        sample_caretaker.availability.is_available = True
        sample_caretaker.availability.current_load = 1
        sample_caretaker.max_concurrent_tasks = 3

        assert sample_caretaker.is_available_for_task() is True

    def test_not_available_when_load_at_max(self, sample_caretaker):
        """Test that worker is not available when load at max."""
        sample_caretaker.availability.is_available = False
        sample_caretaker.availability.current_load = 3
        sample_caretaker.max_concurrent_tasks = 3

        assert sample_caretaker.is_available_for_task() is False

    def test_not_available_when_availability_is_false(self, sample_veterinarian):
        """Test that worker is not available when is_available is False."""
        sample_veterinarian.availability.is_available = False
        sample_veterinarian.availability.current_load = 0

        assert sample_veterinarian.is_available_for_task() is False

    def test_not_available_when_no_availability_object(self):
        """Test that worker is not available when no availability object."""
        worker = Worker(
            worker_id="W005",
            name="No Avail",
            role=WorkerRole.CARETAKER
        )
        worker.availability = None

        assert worker.is_available_for_task() is False


class TestWorkerAssignTask:
    """Test assign_task() method."""

    def test_assign_task_increments_current_load(self, sample_caretaker):
        """Test that assign_task() increments current_load."""
        initial_load = sample_caretaker.availability.current_load
        sample_caretaker.assign_task()

        assert sample_caretaker.availability.current_load == initial_load + 1

    def test_assign_task_updates_availability_status(self):
        """Test that assign_task() updates availability status."""
        worker = Worker(
            worker_id="W006",
            name="Test",
            role=WorkerRole.CLEANER,
            max_concurrent_tasks=2
        )

        worker.availability.current_load = 1
        worker.availability.is_available = True

        worker.assign_task()

        assert worker.availability.current_load == 2
        assert worker.availability.is_available is False  # At max capacity

    def test_assign_task_when_below_capacity(self):
        """Test assign_task when still below capacity."""
        worker = Worker(
            worker_id="W007",
            name="Test",
            role=WorkerRole.VETERINARIAN,
            max_concurrent_tasks=3
        )

        worker.availability.current_load = 1
        worker.assign_task()

        assert worker.availability.current_load == 2
        assert worker.availability.is_available is True  # Still below max


class TestWorkerCompleteTask:
    """Test complete_task() method."""

    def test_complete_task_decrements_current_load(self, sample_caretaker):
        """Test that complete_task() decrements current_load."""
        sample_caretaker.availability.current_load = 2
        sample_caretaker.complete_task(success=True)

        assert sample_caretaker.availability.current_load == 1

    def test_complete_task_updates_availability_status(self):
        """Test that complete_task() updates availability status."""
        worker = Worker(
            worker_id="W008",
            name="Test",
            role=WorkerRole.CLEANER,
            max_concurrent_tasks=2
        )

        worker.availability.current_load = 2
        worker.availability.is_available = False

        worker.complete_task(success=True)

        assert worker.availability.current_load == 1
        assert worker.availability.is_available is True  # Below max capacity

    def test_complete_task_success_increments_completed(self):
        """Test that complete_task() with success increments tasks_completed."""
        worker = Worker(
            worker_id="W009",
            name="Test",
            role=WorkerRole.VETERINARIAN,
            max_concurrent_tasks=2
        )

        initial_completed = worker.tasks_completed
        worker.availability.current_load = 1
        worker.complete_task(success=True)

        assert worker.tasks_completed == initial_completed + 1
        assert worker.tasks_failed == 0

    def test_complete_task_failure_increments_failed(self):
        """Test that complete_task() with failure increments tasks_failed."""
        worker = Worker(
            worker_id="W010",
            name="Test",
            role=WorkerRole.CARETAKER,
            max_concurrent_tasks=3
        )

        initial_failed = worker.tasks_failed
        worker.availability.current_load = 2
        worker.complete_task(success=False)

        assert worker.tasks_failed == initial_failed + 1
        assert worker.availability.current_load == 1

    def test_complete_task_does_not_go_below_zero(self):
        """Test that complete_task() does not make load negative."""
        worker = Worker(
            worker_id="W011",
            name="Test",
            role=WorkerRole.CLEANER,
            max_concurrent_tasks=2
        )

        worker.availability.current_load = 0
        worker.complete_task(success=True)

        assert worker.availability.current_load == 0  # Should not go negative


class TestWorkerEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_worker_with_empty_competencies(self):
        """Test worker with empty competencies."""
        worker = Worker(
            worker_id="W012",
            name="No Skills",
            role=WorkerRole.RECEPTION,
            competencies=set()
        )

        assert len(worker.competencies) == 0
        assert worker.can_handle_task(TaskType.FEED.value) is False

    def test_worker_with_max_concurrent_tasks_zero(self):
        """Test worker with max_concurrent_tasks of 0."""
        worker = Worker(
            worker_id="W013",
            name="No Tasks",
            role=WorkerRole.COORDINATOR,
            max_concurrent_tasks=0
        )

        assert worker.is_available_for_task() is False

    def test_worker_statistics_tracking(self):
        """Test worker statistics are tracked correctly."""
        worker = Worker(
            worker_id="W014",
            name="Stats Test",
            role=WorkerRole.CARETAKER,
            max_concurrent_tasks=3
        )

        # Complete some tasks
        worker.availability.current_load = 3
        worker.complete_task(success=True)
        worker.complete_task(success=True)
        worker.complete_task(success=False)

        assert worker.tasks_completed == 2
        assert worker.tasks_failed == 1
        assert worker.availability.current_load == 0

    def test_worker_with_preferences(self):
        """Test worker with preferences dict."""
        worker = Worker(
            worker_id="W015",
            name="Preferences",
            role=WorkerRole.VETERINARIAN,
            preferences={"shift": "morning", "max_animals_per_day": 10}
        )

        assert worker.preferences["shift"] == "morning"
        assert worker.preferences["max_animals_per_day"] == 10

    def test_worker_availability_object_initialization(self):
        """Test WorkerAvailability object initialization."""
        availability = WorkerAvailability(
            worker_id="W016",
            schedule={"Monday": ["08:00-16:00"]},
            is_available=True,
            current_load=1,
            max_concurrent_tasks=3
        )

        assert availability.worker_id == "W016"
        assert "Monday" in availability.schedule
        assert availability.is_available is True
        assert availability.current_load == 1
