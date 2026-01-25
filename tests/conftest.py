"""Shared pytest fixtures for all tests."""

import pytest
from datetime import datetime, timedelta
from models.animal import Animal
from models.task import Task
from models.worker import Worker, WorkerAvailability
from models.room import Room
from models.adoption_application import AdoptionApplication
from models.enums import (
    Priority, WorkerRole, TaskStatus, TaskType,
    AnimalHealthStatus, AnimalAdoptionStatus,
    RoomState, RoomType, ApplicationStatus
)


@pytest.fixture
def sample_dog():
    """Create a sample dog for testing."""
    return Animal(
        animal_id="DOG001",
        name="Buddy",
        species="dog",
        breed="Golden Retriever",
        age=3,
        sex="male",
        health_status=AnimalHealthStatus.HEALTHY,
        vaccination_status={"rabies": "2024-01-15", "distemper": "2024-01-15"},
        next_vaccination_due="2025-01-15",
        dietary_requirements="standard",
        behavioral_notes="Friendly and energetic",
        adoption_status=AnimalAdoptionStatus.AVAILABLE,
        intake_date=datetime(2024, 1, 1, 10, 0, 0)
    )


@pytest.fixture
def sample_cat():
    """Create a sample cat for testing."""
    return Animal(
        animal_id="CAT001",
        name="Whiskers",
        species="cat",
        breed="Siamese",
        age=2,
        sex="female",
        health_status=AnimalHealthStatus.HEALTHY,
        vaccination_status={"rabies": "2024-02-10"},
        next_vaccination_due="2025-02-10",
        dietary_requirements="grain-free",
        behavioral_notes="Independent, enjoys quiet",
        adoption_status=AnimalAdoptionStatus.AVAILABLE,
        intake_date=datetime(2024, 2, 1, 14, 30, 0)
    )


@pytest.fixture
def sick_animal():
    """Create a sick animal for testing."""
    return Animal(
        animal_id="DOG002",
        name="Max",
        species="dog",
        breed="Labrador",
        age=5,
        sex="male",
        health_status=AnimalHealthStatus.SICK,
        vaccination_status={},
        medications=["Antibiotics", "Pain reliever"],
        dietary_requirements="sensitive stomach",
        behavioral_notes="Lethargic, needs rest",
        adoption_status=AnimalAdoptionStatus.NOT_AVAILABLE,
        intake_date=datetime(2024, 3, 1, 9, 0, 0)
    )


@pytest.fixture
def sample_feed_task():
    """Create a sample feeding task."""
    return Task(
        task_id="FEED-001",
        task_type=TaskType.FEED,
        priority=Priority.NORMAL,
        status=TaskStatus.PENDING,
        created_at=datetime.now(),
        parameters={"animal_id": "DOG001", "meal_type": "breakfast", "portion_size": "medium"}
    )


@pytest.fixture
def sample_walk_task():
    """Create a sample walking task."""
    return Task(
        task_id="WALK-001",
        task_type=TaskType.WALK,
        priority=Priority.NORMAL,
        status=TaskStatus.PENDING,
        created_at=datetime.now(),
        parameters={"animal_id": "DOG001", "duration_minutes": 30}
    )


@pytest.fixture
def sample_caretaker():
    """Create a sample caretaker worker."""
    return Worker(
        worker_id="CARE001",
        name="John Smith",
        role=WorkerRole.CARETAKER,
        competencies={TaskType.FEED.value, TaskType.WALK.value},
        max_concurrent_tasks=3
    )


@pytest.fixture
def sample_veterinarian():
    """Create a sample veterinarian worker."""
    return Worker(
        worker_id="VET001",
        name="Dr. Sarah Johnson",
        role=WorkerRole.VETERINARIAN,
        competencies={TaskType.HEALTH_CHECK.value, TaskType.VACCINATION.value, TaskType.INITIAL_CHECKUP.value},
        max_concurrent_tasks=2
    )


@pytest.fixture
def sample_cleaner():
    """Create a sample cleaner worker."""
    return Worker(
        worker_id="CLEAN001",
        name="Mike Davis",
        role=WorkerRole.CLEANER,
        competencies={TaskType.CLEAN.value},
        max_concurrent_tasks=4
    )


@pytest.fixture
def sample_room():
    """Create a sample room for testing."""
    return Room(
        room_id="ROOM001",
        name="Housing Unit A",
        room_type=RoomType.ANIMAL_HOUSING,
        capacity=4,
        current_occupants=[],
        cleanliness_state=RoomState.CLEAN,
        last_cleaned=datetime.now(),
        daily_clean_time="08:00"
    )


@pytest.fixture
def dirty_room():
    """Create a dirty room for testing."""
    return Room(
        room_id="ROOM002",
        name="Housing Unit B",
        room_type=RoomType.ANIMAL_HOUSING,
        capacity=6,
        current_occupants=["DOG001", "CAT001", "DOG002"],
        cleanliness_state=RoomState.DIRTY,
        last_cleaned=datetime.now() - timedelta(hours=25),
        daily_clean_time="10:00"
    )


@pytest.fixture
def sample_adoption_application():
    """Create a sample adoption application."""
    return AdoptionApplication(
        application_id="APP001",
        applicant_id="APPL001",
        applicant_name="Jane Doe",
        applicant_age=30,
        applicant_contact="jane.doe@email.com",
        applicant_address="123 Main St",
        animal_id="DOG001",
        status=ApplicationStatus.SUBMITTED,
        submitted_at=datetime.now(),
        home_type="house",
        has_yard=True,
        has_previous_pet_experience=True
    )


@pytest.fixture
def approved_adoption_application():
    """Create an approved adoption application."""
    return AdoptionApplication(
        application_id="APP002",
        applicant_id="APPL002",
        applicant_name="Bob Smith",
        applicant_age=35,
        applicant_contact="bob.smith@email.com",
        applicant_address="456 Oak Ave",
        animal_id="CAT001",
        status=ApplicationStatus.APPROVED,
        submitted_at=datetime.now() - timedelta(days=3),
        home_type="apartment",
        has_yard=False,
        other_pets=["cat"],
        has_previous_pet_experience=True
    )


@pytest.fixture
def sample_task_data():
    """Sample task data for testing validators and builders."""
    return {
        "task_id": "TASK-001",
        "task_type": "feed",
        "priority": 3,
        "target_id": "DOG001",
        "status": "pending",
        "description": "Feed the dog",
        "parameters": {"meal_type": "breakfast"}
    }


@pytest.fixture
def sample_animal_data():
    """Sample animal data for testing validators."""
    return {
        "id": "DOG003",
        "name": "Charlie",
        "species": "dog",
        "breed": "Beagle",
        "age": 4,
        "sex": "male",
        "health_status": "healthy",
        "adoption_status": "available"
    }


@pytest.fixture
def sample_worker_data():
    """Sample worker data for testing validators."""
    return {
        "worker_id": "WORK001",
        "name": "Test Worker",
        "role": "caretaker",
        "competencies": ["feed", "walk"],
        "max_concurrent_tasks": 3
    }


@pytest.fixture
def sample_room_data():
    """Sample room data for testing validators."""
    return {
        "room_id": "ROOM003",
        "name": "Test Room",
        "room_type": "animal_housing",
        "capacity": 5,
        "state": "clean"
    }
