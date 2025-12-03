from enum import Enum


class Priority(Enum):
    URGENT = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class WorkerRole(Enum):
    COORDINATOR = "coordinator"
    CARETAKER = "caretaker"
    CLEANER = "cleaner"
    VETERINARIAN = "veterinarian"
    RECEPTION = "reception"
    ADOPTION = "adoption"


class TaskStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(Enum):
    FEED = "feed"
    WALK = "walk"
    CLEAN = "clean"
    VACCINATION = "vaccination"
    HEALTH_CHECK = "health_check"
    INITIAL_CHECKUP = "initial_checkup"
    ADOPTION_APPLICATION = "adoption_application"


class AnimalHealthStatus(Enum):
    HEALTHY = "healthy"
    SICK = "sick"
    CHRONIC_CONDITION = "chronic_condition"
    RECOVERING = "recovering"
    NEEDS_CHECKUP = "needs_checkup"


class AnimalAdoptionStatus(Enum):
    AVAILABLE = "available"
    PENDING = "pending"
    ADOPTED = "adopted"
    NOT_AVAILABLE = "not_available"


class RoomState(Enum):
    CLEAN = "clean"
    DIRTY = "dirty"
    CLEANING_IN_PROGRESS = "cleaning_in_progress"


class RoomType(Enum):
    ANIMAL_HOUSING = "animal_housing"
    MEDICAL = "medical"
    QUARANTINE = "quarantine"
    COMMON = "common"


class ApplicationStatus(Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
