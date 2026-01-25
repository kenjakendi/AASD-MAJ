"""Unit tests for the Animal model."""

import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time
from models.animal import Animal
from models.enums import AnimalHealthStatus, AnimalAdoptionStatus


class TestAnimalInitialization:
    """Test Animal model initialization."""

    def test_animal_creation_with_required_fields(self):
        """Test creating an animal with only required fields."""
        animal = Animal(
            animal_id="TEST001",
            name="Fluffy",
            species="cat",
            breed="Persian",
            age=3,
            sex="female"
        )

        assert animal.animal_id == "TEST001"
        assert animal.name == "Fluffy"
        assert animal.species == "cat"
        assert animal.breed == "Persian"
        assert animal.age == 3
        assert animal.sex == "female"
        assert animal.health_status == AnimalHealthStatus.HEALTHY
        assert animal.adoption_status == AnimalAdoptionStatus.AVAILABLE

    def test_animal_creation_with_all_fields(self, sample_dog):
        """Test creating an animal with all fields."""
        assert sample_dog.animal_id == "DOG001"
        assert sample_dog.name == "Buddy"
        assert sample_dog.species == "dog"
        assert sample_dog.breed == "Golden Retriever"
        assert sample_dog.age == 3
        assert sample_dog.health_status == AnimalHealthStatus.HEALTHY
        assert sample_dog.adoption_status == AnimalAdoptionStatus.AVAILABLE
        assert len(sample_dog.vaccination_status) > 0


class TestAnimalSerialization:
    """Test Animal serialization and deserialization."""

    def test_to_dict_produces_correct_structure(self, sample_dog):
        """Test that to_dict() produces correct JSON structure."""
        data = sample_dog.to_dict()

        assert data['id'] == "DOG001"
        assert data['name'] == "Buddy"
        assert data['species'] == "dog"
        assert data['breed'] == "Golden Retriever"
        assert data['age'] == 3
        assert data['sex'] == "male"
        assert data['health_status'] == "healthy"
        assert data['adoption_status'] == "available"
        assert 'vaccination_status' in data
        assert 'dietary_requirements' in data

    def test_from_dict_restores_object_correctly(self, sample_dog):
        """Test that from_dict() restores object correctly."""
        data = sample_dog.to_dict()
        restored = Animal.from_dict(data)

        assert restored.animal_id == sample_dog.animal_id
        assert restored.name == sample_dog.name
        assert restored.species == sample_dog.species
        assert restored.breed == sample_dog.breed
        assert restored.age == sample_dog.age
        assert restored.sex == sample_dog.sex
        assert restored.health_status == sample_dog.health_status
        assert restored.adoption_status == sample_dog.adoption_status

    def test_roundtrip_serialization_maintains_integrity(self, sample_dog):
        """Test that roundtrip serialization maintains data integrity."""
        data = sample_dog.to_dict()
        restored = Animal.from_dict(data)
        data2 = restored.to_dict()

        assert data == data2

    def test_serialization_handles_none_values(self):
        """Test serialization with None values for optional fields."""
        animal = Animal(
            animal_id="TEST002",
            name="Rex",
            species="dog",
            breed="Mixed",
            age=2,
            sex="male"
        )

        data = animal.to_dict()
        assert data['last_fed'] is None
        assert data['last_walked'] is None
        assert data['last_health_check'] is None

    def test_deserialization_with_datetime_strings(self):
        """Test deserializing animals with datetime strings."""
        data = {
            'id': 'TEST003',
            'name': 'Mittens',
            'species': 'cat',
            'breed': 'Tabby',
            'age': 1,
            'sex': 'female',
            'health_status': 'healthy',
            'adoption_status': 'available',
            'last_fed': '2024-01-15T10:30:00',
            'last_walked': '2024-01-15T09:00:00',
            'last_health_check': '2024-01-10T14:00:00',
            'intake_date': '2024-01-01T08:00:00'
        }

        animal = Animal.from_dict(data)
        assert isinstance(animal.last_fed, datetime)
        assert isinstance(animal.last_walked, datetime)
        assert isinstance(animal.last_health_check, datetime)
        assert isinstance(animal.intake_date, datetime)


class TestAnimalNeedsFeeding:
    """Test needs_feeding() method."""

    @freeze_time("2024-01-15 12:00:00")
    def test_needs_feeding_when_never_fed(self):
        """Test that animal needs feeding when never fed."""
        animal = Animal(
            animal_id="TEST004",
            name="Hungry",
            species="dog",
            breed="Beagle",
            age=2,
            sex="male"
        )

        assert animal.needs_feeding() is True

    @freeze_time("2024-01-15 12:00:00")
    def test_needs_feeding_when_interval_exceeded(self):
        """Test that animal needs feeding when time interval exceeded."""
        animal = Animal(
            animal_id="TEST005",
            name="Hungry",
            species="dog",
            breed="Beagle",
            age=2,
            sex="male",
            last_fed=datetime(2024, 1, 15, 3, 0, 0)  # 9 hours ago
        )

        assert animal.needs_feeding(interval_hours=8) is True

    @freeze_time("2024-01-15 12:00:00")
    def test_does_not_need_feeding_when_recently_fed(self):
        """Test that animal doesn't need feeding when recently fed."""
        animal = Animal(
            animal_id="TEST006",
            name="Full",
            species="cat",
            breed="Siamese",
            age=1,
            sex="female",
            last_fed=datetime(2024, 1, 15, 10, 0, 0)  # 2 hours ago
        )

        assert animal.needs_feeding(interval_hours=8) is False

    @freeze_time("2024-01-15 12:00:00")
    def test_needs_feeding_exact_boundary(self):
        """Test feeding need at exact boundary."""
        animal = Animal(
            animal_id="TEST007",
            name="Boundary",
            species="dog",
            breed="Lab",
            age=3,
            sex="male",
            last_fed=datetime(2024, 1, 15, 4, 0, 0)  # Exactly 8 hours ago
        )

        assert animal.needs_feeding(interval_hours=8) is True


class TestAnimalNeedsWalk:
    """Test needs_walk() method."""

    @freeze_time("2024-01-15 12:00:00")
    def test_needs_walk_for_dog_when_never_walked(self):
        """Test that dog needs walk when never walked."""
        animal = Animal(
            animal_id="TEST008",
            name="Active",
            species="dog",
            breed="Border Collie",
            age=2,
            sex="male"
        )

        assert animal.needs_walk() is True

    @freeze_time("2024-01-15 12:00:00")
    def test_needs_walk_for_dog_when_interval_exceeded(self):
        """Test that dog needs walk when interval exceeded."""
        animal = Animal(
            animal_id="TEST009",
            name="Runner",
            species="dog",
            breed="Husky",
            age=3,
            sex="female",
            last_walked=datetime(2024, 1, 15, 5, 0, 0)  # 7 hours ago
        )

        assert animal.needs_walk(interval_hours=6) is True

    @freeze_time("2024-01-15 12:00:00")
    def test_does_not_need_walk_when_recently_walked(self):
        """Test that dog doesn't need walk when recently walked."""
        animal = Animal(
            animal_id="TEST010",
            name="Tired",
            species="dog",
            breed="Bulldog",
            age=4,
            sex="male",
            last_walked=datetime(2024, 1, 15, 10, 0, 0)  # 2 hours ago
        )

        assert animal.needs_walk(interval_hours=6) is False

    def test_cat_never_needs_walk(self):
        """Test that non-dog species never need walks."""
        animal = Animal(
            animal_id="TEST011",
            name="Lazy",
            species="cat",
            breed="Persian",
            age=2,
            sex="female"
        )

        assert animal.needs_walk() is False

    def test_other_species_never_need_walk(self):
        """Test that other species never need walks."""
        animal = Animal(
            animal_id="TEST012",
            name="Hoppy",
            species="rabbit",
            breed="Holland Lop",
            age=1,
            sex="male"
        )

        assert animal.needs_walk() is False


class TestAnimalNeedsHealthCheck:
    """Test needs_health_check() method."""

    @freeze_time("2024-01-15 12:00:00")
    def test_sick_animal_needs_health_check(self, sick_animal):
        """Test that sick animal needs health check."""
        assert sick_animal.needs_health_check() is True

    def test_animal_needing_checkup_needs_health_check(self):
        """Test that animal with NEEDS_CHECKUP status needs health check."""
        animal = Animal(
            animal_id="TEST013",
            name="Checkup",
            species="dog",
            breed="Poodle",
            age=5,
            sex="female",
            health_status=AnimalHealthStatus.NEEDS_CHECKUP
        )

        assert animal.needs_health_check() is True

    @freeze_time("2024-01-15 12:00:00")
    def test_needs_health_check_when_never_checked(self):
        """Test that animal needs health check when never checked."""
        animal = Animal(
            animal_id="TEST014",
            name="New",
            species="cat",
            breed="Tabby",
            age=1,
            sex="male"
        )

        assert animal.needs_health_check() is True

    @freeze_time("2024-01-15 12:00:00")
    def test_needs_health_check_when_30_days_exceeded(self):
        """Test that animal needs health check after 30 days."""
        animal = Animal(
            animal_id="TEST015",
            name="Overdue",
            species="dog",
            breed="Terrier",
            age=3,
            sex="male",
            health_status=AnimalHealthStatus.HEALTHY,
            last_health_check=datetime(2023, 12, 10, 10, 0, 0)  # 36 days ago
        )

        assert animal.needs_health_check() is True

    @freeze_time("2024-01-15 12:00:00")
    def test_does_not_need_health_check_when_recent(self):
        """Test that animal doesn't need health check when recently checked."""
        animal = Animal(
            animal_id="TEST016",
            name="Healthy",
            species="cat",
            breed="Maine Coon",
            age=2,
            sex="female",
            health_status=AnimalHealthStatus.HEALTHY,
            last_health_check=datetime(2024, 1, 1, 10, 0, 0)  # 14 days ago
        )

        assert animal.needs_health_check() is False


class TestAnimalNeedsVaccination:
    """Test needs_vaccination() method."""

    @freeze_time("2024-01-15")
    def test_needs_vaccination_when_due_date_reached(self):
        """Test that animal needs vaccination when due date is reached."""
        animal = Animal(
            animal_id="TEST017",
            name="Vax Due",
            species="dog",
            breed="Lab",
            age=2,
            sex="male",
            next_vaccination_due="2024-01-15"
        )

        assert animal.needs_vaccination() is True

    @freeze_time("2024-01-15")
    def test_needs_vaccination_when_overdue(self):
        """Test that animal needs vaccination when overdue."""
        animal = Animal(
            animal_id="TEST018",
            name="Overdue",
            species="cat",
            breed="Siamese",
            age=3,
            sex="female",
            next_vaccination_due="2024-01-01"
        )

        assert animal.needs_vaccination() is True

    @freeze_time("2024-01-15")
    def test_does_not_need_vaccination_when_future(self):
        """Test that animal doesn't need vaccination when date is in future."""
        animal = Animal(
            animal_id="TEST019",
            name="Future Vax",
            species="dog",
            breed="Beagle",
            age=1,
            sex="male",
            next_vaccination_due="2024-02-15"
        )

        assert animal.needs_vaccination() is False

    def test_does_not_need_vaccination_when_no_due_date(self):
        """Test that animal doesn't need vaccination when no due date set."""
        animal = Animal(
            animal_id="TEST020",
            name="No Vax",
            species="cat",
            breed="Persian",
            age=2,
            sex="female",
            next_vaccination_due=None
        )

        assert animal.needs_vaccination() is False

    def test_handles_invalid_date_format(self):
        """Test that invalid date format returns False."""
        animal = Animal(
            animal_id="TEST021",
            name="Invalid Date",
            species="dog",
            breed="Poodle",
            age=3,
            sex="male",
            next_vaccination_due="invalid-date"
        )

        assert animal.needs_vaccination() is False


class TestAnimalStateUpdates:
    """Test state update methods."""

    @freeze_time("2024-01-15 12:30:00")
    def test_update_feed_state(self):
        """Test that update_feed_state() sets last_fed timestamp."""
        animal = Animal(
            animal_id="TEST022",
            name="Update Test",
            species="dog",
            breed="Lab",
            age=2,
            sex="male"
        )

        animal.update_feed_state()
        assert animal.last_fed is not None
        assert animal.last_fed == datetime(2024, 1, 15, 12, 30, 0)

    @freeze_time("2024-01-15 14:00:00")
    def test_update_walk_state(self):
        """Test that update_walk_state() sets last_walked timestamp."""
        animal = Animal(
            animal_id="TEST023",
            name="Walk Test",
            species="dog",
            breed="Beagle",
            age=3,
            sex="female"
        )

        animal.update_walk_state()
        assert animal.last_walked is not None
        assert animal.last_walked == datetime(2024, 1, 15, 14, 0, 0)

    @freeze_time("2024-01-15 16:00:00")
    def test_update_health_status(self):
        """Test that update_health_status() updates status and timestamp."""
        animal = Animal(
            animal_id="TEST024",
            name="Health Test",
            species="cat",
            breed="Siamese",
            age=2,
            sex="male",
            health_status=AnimalHealthStatus.NEEDS_CHECKUP
        )

        animal.update_health_status(AnimalHealthStatus.HEALTHY)
        assert animal.health_status == AnimalHealthStatus.HEALTHY
        assert animal.last_health_check == datetime(2024, 1, 15, 16, 0, 0)

    @freeze_time("2024-01-15 10:00:00")
    def test_update_health_status_to_sick(self):
        """Test updating health status to SICK."""
        animal = Animal(
            animal_id="TEST025",
            name="Sick Test",
            species="dog",
            breed="Poodle",
            age=4,
            sex="female",
            health_status=AnimalHealthStatus.HEALTHY
        )

        animal.update_health_status(AnimalHealthStatus.SICK)
        assert animal.health_status == AnimalHealthStatus.SICK
        assert animal.last_health_check == datetime(2024, 1, 15, 10, 0, 0)


class TestAnimalEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_animal_with_empty_vaccination_status(self):
        """Test animal with empty vaccination status."""
        animal = Animal(
            animal_id="TEST026",
            name="No Vax",
            species="dog",
            breed="Mixed",
            age=1,
            sex="male",
            vaccination_status={}
        )

        data = animal.to_dict()
        assert data['vaccination_status'] == {}

    def test_animal_with_empty_medications(self):
        """Test animal with empty medications list."""
        animal = Animal(
            animal_id="TEST027",
            name="No Meds",
            species="cat",
            breed="Tabby",
            age=2,
            sex="female",
            medications=[]
        )

        data = animal.to_dict()
        assert data['medications'] == []

    def test_animal_age_zero(self):
        """Test animal with age zero (newborn)."""
        animal = Animal(
            animal_id="TEST028",
            name="Newborn",
            species="dog",
            breed="Chihuahua",
            age=0,
            sex="male"
        )

        assert animal.age == 0

    def test_animal_with_chronic_condition(self):
        """Test animal with chronic condition."""
        animal = Animal(
            animal_id="TEST029",
            name="Chronic",
            species="cat",
            breed="Persian",
            age=10,
            sex="female",
            health_status=AnimalHealthStatus.CHRONIC_CONDITION
        )

        assert animal.health_status == AnimalHealthStatus.CHRONIC_CONDITION

    def test_animal_status_not_available(self):
        """Test animal with NOT_AVAILABLE adoption status."""
        animal = Animal(
            animal_id="TEST030",
            name="Not Available",
            species="dog",
            breed="Lab",
            age=5,
            sex="male",
            adoption_status=AnimalAdoptionStatus.NOT_AVAILABLE
        )

        assert animal.adoption_status == AnimalAdoptionStatus.NOT_AVAILABLE
