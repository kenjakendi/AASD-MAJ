"""Unit tests for the Room model."""

import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time
from models.room import Room
from models.enums import RoomState, RoomType


class TestRoomInitialization:
    """Test Room model initialization."""

    def test_room_creation_with_required_fields(self):
        """Test creating a room with only required fields."""
        room = Room(
            room_id="R001",
            name="Test Room",
            room_type=RoomType.ANIMAL_HOUSING,
            capacity=5
        )

        assert room.room_id == "R001"
        assert room.name == "Test Room"
        assert room.room_type == RoomType.ANIMAL_HOUSING
        assert room.capacity == 5
        assert room.cleanliness_state == RoomState.CLEAN

    def test_room_creation_with_all_fields(self, sample_room):
        """Test creating a room with all fields."""
        assert sample_room.room_id == "ROOM001"
        assert sample_room.name == "Housing Unit A"
        assert sample_room.capacity == 4
        assert sample_room.cleanliness_state == RoomState.CLEAN
        assert isinstance(sample_room.current_occupants, list)


class TestRoomSerialization:
    """Test Room serialization and deserialization."""

    def test_to_dict_produces_correct_structure(self, sample_room):
        """Test that to_dict() produces correct JSON structure."""
        data = sample_room.to_dict()

        assert data['id'] == "ROOM001"
        assert data['name'] == "Housing Unit A"
        assert data['type'] == "animal_housing"
        assert data['capacity'] == 4
        assert data['cleanliness_state'] == "clean"
        assert 'current_occupants' in data

    def test_from_dict_restores_object_correctly(self, sample_room):
        """Test that from_dict() restores object correctly."""
        data = sample_room.to_dict()
        restored = Room.from_dict(data)

        assert restored.room_id == sample_room.room_id
        assert restored.name == sample_room.name
        assert restored.room_type == sample_room.room_type
        assert restored.capacity == sample_room.capacity
        assert restored.cleanliness_state == sample_room.cleanliness_state

    def test_roundtrip_serialization_maintains_integrity(self, dirty_room):
        """Test that roundtrip serialization maintains data integrity."""
        data = dirty_room.to_dict()
        restored = Room.from_dict(data)
        data2 = restored.to_dict()

        assert data['id'] == data2['id']
        assert data['cleanliness_state'] == data2['cleanliness_state']
        assert data['current_occupants'] == data2['current_occupants']


class TestRoomNeedsCleaning:
    """Test needs_cleaning() method."""

    def test_needs_cleaning_when_dirty(self, dirty_room):
        """Test that dirty room needs cleaning."""
        assert dirty_room.needs_cleaning() is True

    @freeze_time("2024-01-15 12:00:00")
    def test_needs_cleaning_when_never_cleaned(self):
        """Test that room needs cleaning when never cleaned."""
        room = Room(
            room_id="R002",
            name="Never Cleaned",
            room_type=RoomType.ANIMAL_HOUSING,
            capacity=4,
            last_cleaned=None
        )

        assert room.needs_cleaning() is True

    @freeze_time("2024-01-15 12:00:00")
    def test_needs_cleaning_when_frequency_exceeded(self):
        """Test that room needs cleaning when frequency exceeded."""
        room = Room(
            room_id="R003",
            name="Overdue",
            room_type=RoomType.ANIMAL_HOUSING,
            capacity=4,
            cleanliness_state=RoomState.CLEAN,
            last_cleaned=datetime(2024, 1, 14, 10, 0, 0),  # 26 hours ago
            clean_frequency_hours=24
        )

        assert room.needs_cleaning() is True

    @freeze_time("2024-01-15 12:00:00")
    def test_does_not_need_cleaning_when_recent(self, sample_room):
        """Test that room doesn't need cleaning when recently cleaned."""
        sample_room.cleanliness_state = RoomState.CLEAN
        sample_room.last_cleaned = datetime(2024, 1, 15, 10, 0, 0)  # 2 hours ago
        sample_room.clean_frequency_hours = 24

        assert sample_room.needs_cleaning() is False


class TestRoomIsScheduledForCleaning:
    """Test is_scheduled_for_cleaning() method."""

    @freeze_time("2024-01-15 08:15:00")
    def test_is_scheduled_when_within_window(self):
        """Test room is scheduled when within 30 min window."""
        room = Room(
            room_id="R004",
            name="Scheduled",
            room_type=RoomType.ANIMAL_HOUSING,
            capacity=4,
            daily_clean_time="08:00"
        )

        assert room.is_scheduled_for_cleaning() is True

    @freeze_time("2024-01-15 10:00:00")
    def test_not_scheduled_when_outside_window(self):
        """Test room is not scheduled when outside window."""
        room = Room(
            room_id="R005",
            name="Not Scheduled",
            room_type=RoomType.ANIMAL_HOUSING,
            capacity=4,
            daily_clean_time="08:00"
        )

        assert room.is_scheduled_for_cleaning() is False

    @freeze_time("2024-01-15 07:50:00")
    def test_is_scheduled_before_clean_time(self):
        """Test room is scheduled 10 min before clean time."""
        room = Room(
            room_id="R006",
            name="Before Time",
            room_type=RoomType.ANIMAL_HOUSING,
            capacity=4,
            daily_clean_time="08:00"
        )

        assert room.is_scheduled_for_cleaning() is True


class TestRoomStateTransitions:
    """Test room state transition methods."""

    def test_mark_dirty_changes_state(self, sample_room):
        """Test that mark_dirty() changes state to DIRTY."""
        sample_room.cleanliness_state = RoomState.CLEAN
        sample_room.mark_dirty()

        assert sample_room.cleanliness_state == RoomState.DIRTY

    def test_mark_cleaning_in_progress_changes_state(self, sample_room):
        """Test that mark_cleaning_in_progress() changes state."""
        sample_room.mark_cleaning_in_progress()

        assert sample_room.cleanliness_state == RoomState.CLEANING_IN_PROGRESS

    @freeze_time("2024-01-15 14:00:00")
    def test_mark_clean_changes_state_and_updates_timestamp(self, dirty_room):
        """Test that mark_clean() changes state and updates timestamp."""
        dirty_room.mark_clean()

        assert dirty_room.cleanliness_state == RoomState.CLEAN
        assert dirty_room.last_cleaned == datetime(2024, 1, 15, 14, 0, 0)


class TestRoomOccupancy:
    """Test room occupancy management methods."""

    def test_add_occupant_to_empty_room(self, sample_room):
        """Test adding occupant to empty room."""
        result = sample_room.add_occupant("DOG001")

        assert result is True
        assert "DOG001" in sample_room.current_occupants
        assert len(sample_room.current_occupants) == 1

    def test_add_multiple_occupants(self, sample_room):
        """Test adding multiple occupants."""
        sample_room.add_occupant("DOG001")
        sample_room.add_occupant("CAT001")
        sample_room.add_occupant("DOG002")

        assert len(sample_room.current_occupants) == 3
        assert "DOG001" in sample_room.current_occupants
        assert "CAT001" in sample_room.current_occupants
        assert "DOG002" in sample_room.current_occupants

    def test_add_occupant_when_full(self):
        """Test adding occupant when room is at capacity."""
        room = Room(
            room_id="R007",
            name="Small Room",
            room_type=RoomType.ANIMAL_HOUSING,
            capacity=2,
            current_occupants=["DOG001", "CAT001"]
        )

        result = room.add_occupant("DOG002")

        assert result is False
        assert len(room.current_occupants) == 2
        assert "DOG002" not in room.current_occupants

    def test_add_duplicate_occupant(self, sample_room):
        """Test that adding duplicate occupant doesn't create duplicate."""
        sample_room.add_occupant("DOG001")
        sample_room.add_occupant("DOG001")

        assert len(sample_room.current_occupants) == 1

    def test_remove_occupant(self):
        """Test removing occupant from room."""
        room = Room(
            room_id="R008",
            name="Test Room",
            room_type=RoomType.ANIMAL_HOUSING,
            capacity=4,
            current_occupants=["DOG001", "CAT001"]
        )

        room.remove_occupant("DOG001")

        assert "DOG001" not in room.current_occupants
        assert "CAT001" in room.current_occupants
        assert len(room.current_occupants) == 1

    def test_remove_non_existent_occupant(self, sample_room):
        """Test removing non-existent occupant does nothing."""
        sample_room.add_occupant("DOG001")
        initial_count = len(sample_room.current_occupants)

        sample_room.remove_occupant("CAT999")

        assert len(sample_room.current_occupants) == initial_count


class TestRoomStatusQueries:
    """Test room status query methods."""

    def test_is_full_when_at_capacity(self):
        """Test that is_full() returns True when at capacity."""
        room = Room(
            room_id="R009",
            name="Full Room",
            room_type=RoomType.ANIMAL_HOUSING,
            capacity=3,
            current_occupants=["DOG001", "CAT001", "DOG002"]
        )

        assert room.is_full() is True

    def test_is_not_full_when_below_capacity(self, sample_room):
        """Test that is_full() returns False when below capacity."""
        sample_room.add_occupant("DOG001")
        sample_room.add_occupant("CAT001")

        assert sample_room.is_full() is False

    def test_is_empty_when_no_occupants(self, sample_room):
        """Test that is_empty() returns True when no occupants."""
        assert sample_room.is_empty() is True

    def test_is_not_empty_when_has_occupants(self):
        """Test that is_empty() returns False when has occupants."""
        room = Room(
            room_id="R010",
            name="Occupied Room",
            room_type=RoomType.ANIMAL_HOUSING,
            capacity=4,
            current_occupants=["DOG001"]
        )

        assert room.is_empty() is False


class TestRoomEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_room_with_zero_capacity(self):
        """Test room with zero capacity."""
        room = Room(
            room_id="R011",
            name="Zero Capacity",
            room_type=RoomType.COMMON,
            capacity=0
        )

        assert room.is_full() is True
        assert room.add_occupant("DOG001") is False

    def test_room_medical_type(self):
        """Test room with MEDICAL type."""
        room = Room(
            room_id="R012",
            name="Medical Room",
            room_type=RoomType.MEDICAL,
            capacity=2
        )

        assert room.room_type == RoomType.MEDICAL

    def test_room_quarantine_type(self):
        """Test room with QUARANTINE type."""
        room = Room(
            room_id="R013",
            name="Quarantine Room",
            room_type=RoomType.QUARANTINE,
            capacity=1
        )

        assert room.room_type == RoomType.QUARANTINE

    def test_room_with_special_cleaning_requirements(self):
        """Test room with special cleaning requirements."""
        room = Room(
            room_id="R014",
            name="Special Clean",
            room_type=RoomType.MEDICAL,
            capacity=2,
            requires_special_cleaning=True,
            special_cleaning_notes="Use disinfectant"
        )

        assert room.requires_special_cleaning is True
        assert room.special_cleaning_notes == "Use disinfectant"

    def test_room_with_custom_clean_frequency(self):
        """Test room with custom cleaning frequency."""
        room = Room(
            room_id="R015",
            name="Frequent Clean",
            room_type=RoomType.QUARANTINE,
            capacity=1,
            clean_frequency_hours=12
        )

        assert room.clean_frequency_hours == 12

    @freeze_time("2024-01-15 12:00:00")
    def test_cleaning_state_lifecycle(self):
        """Test complete cleaning state lifecycle."""
        room = Room(
            room_id="R016",
            name="Lifecycle Test",
            room_type=RoomType.ANIMAL_HOUSING,
            capacity=4,
            cleanliness_state=RoomState.CLEAN,
            last_cleaned=datetime(2024, 1, 14, 12, 0, 0)
        )

        # Room becomes dirty
        room.mark_dirty()
        assert room.cleanliness_state == RoomState.DIRTY
        assert room.needs_cleaning() is True

        # Cleaning starts
        room.mark_cleaning_in_progress()
        assert room.cleanliness_state == RoomState.CLEANING_IN_PROGRESS

        # Cleaning completes
        with freeze_time("2024-01-15 12:30:00"):
            room.mark_clean()
            assert room.cleanliness_state == RoomState.CLEAN
            assert room.last_cleaned == datetime(2024, 1, 15, 12, 30, 0)
