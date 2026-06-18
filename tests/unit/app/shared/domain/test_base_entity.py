from datetime import datetime
from uuid import UUID, uuid4

from pytz import UTC

from app.shared.domain.base_entity import BaseEntity


class ConcreteEntity(BaseEntity):
    def __init__(
        self,
        id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        name: str = "",
    ):
        super().__init__(id, created_at, updated_at)
        self.name = name


class TestBaseEntityCreation:
    def test_auto_generates_uuid(self):
        entity = ConcreteEntity()
        assert isinstance(entity.id, UUID)

    def test_auto_generates_created_at(self):
        entity = ConcreteEntity()
        assert isinstance(entity.created_at, datetime)
        assert entity.created_at.tzinfo is not None

    def test_auto_generates_updated_at(self):
        entity = ConcreteEntity()
        assert isinstance(entity.updated_at, datetime)
        assert entity.updated_at.tzinfo is not None

    def test_created_and_updated_close_on_creation(self):
        entity = ConcreteEntity()
        diff = abs((entity.updated_at - entity.created_at).total_seconds())
        assert diff < 1.0

    def test_timezone_is_utc(self):
        entity = ConcreteEntity()
        assert entity.created_at.tzinfo == UTC
        assert entity.updated_at.tzinfo == UTC

    def test_unique_ids(self):
        e1 = ConcreteEntity()
        e2 = ConcreteEntity()
        assert e1.id != e2.id

    def test_explicit_id(self):
        explicit_id = uuid4()
        entity = ConcreteEntity(id=explicit_id)
        assert entity.id == explicit_id

    def test_explicit_created_at(self):
        dt = datetime.now(UTC)
        entity = ConcreteEntity(created_at=dt)
        assert entity.created_at == dt

    def test_explicit_updated_at(self):
        dt = datetime.now(UTC)
        entity = ConcreteEntity(updated_at=dt)
        assert entity.updated_at == dt

    def test_none_id_auto_generates(self):
        entity = ConcreteEntity(id=None)
        assert isinstance(entity.id, UUID)


class TestBaseEntityEquality:
    def test_same_id_are_equal(self):
        e1 = ConcreteEntity()
        e2 = ConcreteEntity(id=e1.id)
        assert e1 == e2

    def test_different_ids_not_equal(self):
        e1 = ConcreteEntity()
        e2 = ConcreteEntity()
        assert e1 != e2

    def test_not_equal_to_non_entity(self):
        e = ConcreteEntity()
        assert e != "not an entity"
        assert e != 42
        assert e is not None

    def test_not_equal_to_different_subclass(self):
        class SubEntity(ConcreteEntity):
            pass

        e1 = ConcreteEntity()
        e2 = SubEntity(id=e1.id)
        assert not (e1 == e2)


class TestBaseEntityHash:
    def test_hash_equals_hash_of_id(self):
        entity = ConcreteEntity()
        assert hash(entity) == hash(entity.id)

    def test_hash_allows_set_usage(self):
        e1 = ConcreteEntity()
        e2 = ConcreteEntity()
        s = {e1, e2}
        assert len(s) == 2

    def test_set_deduplicates_by_id(self):
        e1 = ConcreteEntity()
        e2 = ConcreteEntity(id=e1.id)
        s = {e1, e2}
        assert len(s) == 1


class TestBaseEntityTouch:
    def test_updates_updated_at(self):
        entity = ConcreteEntity()
        original = entity.updated_at
        entity._touch()  # pyright: ignore
        assert entity.updated_at > original

    def test_does_not_change_created_at(self):
        entity = ConcreteEntity()
        original = entity.created_at
        entity._touch()  # pyright: ignore
        assert entity.created_at == original

    def test_sets_utc_timezone(self):
        entity = ConcreteEntity()
        entity._touch()  # pyright: ignore
        assert entity.updated_at.tzinfo == UTC

    def test_multiple_touches_monotonic(self):
        entity = ConcreteEntity()
        times: list[datetime] = []
        for _ in range(5):
            entity._touch()  # pyright: ignore
            times.append(entity.updated_at)
        for i in range(len(times) - 1):
            assert times[i + 1] >= times[i]

    def test_touch_uses_current_time(self):
        entity = ConcreteEntity()
        before = datetime.now(UTC)
        entity._touch()  # pyright: ignore
        after = datetime.now(UTC)
        assert before <= entity.updated_at <= after
