from datetime import datetime
from uuid import uuid4

from pytz import UTC

from app.shared.domain.base_entity import BaseEntity


class ConcreteEntity(BaseEntity):
    def __init__(self, name: str = ""):
        super().__init__()
        self.name = name


class TestBaseEntityCreation:
    def test_auto_generates_uuid(self):
        e = ConcreteEntity()
        assert e.id is not None
        assert isinstance(e.id, type(uuid4()))

    def test_auto_generates_created_at(self):
        e = ConcreteEntity()
        assert isinstance(e.created_at, datetime)
        assert e.created_at.tzinfo is not None

    def test_auto_generates_updated_at(self):
        e = ConcreteEntity()
        assert isinstance(e.updated_at, datetime)
        assert e.updated_at.tzinfo is not None

    def test_created_and_updated_are_equal_on_creation(self):
        e = ConcreteEntity()
        diff = abs((e.updated_at - e.created_at).total_seconds())
        assert diff < 1.0

    def test_unique_ids_per_instance(self):
        e1 = ConcreteEntity()
        e2 = ConcreteEntity()
        assert e1.id != e2.id

    def test_created_at_differs_across_instances(self):
        e1 = ConcreteEntity()
        e2 = ConcreteEntity()
        assert e1.created_at != e2.created_at
        assert e2.created_at >= e1.created_at


class TestBaseEntityEquality:
    def test_same_id_are_equal(self):
        e1 = ConcreteEntity()
        e2 = ConcreteEntity()
        e2.id = e1.id
        assert e1 == e2

    def test_different_id_are_not_equal(self):
        e1 = ConcreteEntity()
        e2 = ConcreteEntity()
        assert e1 != e2

    def test_not_equal_to_non_entity(self):
        e = ConcreteEntity()
        assert e != "not an entity"
        assert e != 42
        assert e is not None

    def test_not_equal_to_subclass_instance_with_same_id(self):
        class SubEntity(ConcreteEntity):
            pass

        e1 = ConcreteEntity()
        e2 = SubEntity()
        e2.id = e1.id
        assert not (e1 == e2)

    def test_not_equal_to_different_class_same_id(self):
        class OtherEntity(BaseEntity):
            pass

        e1 = ConcreteEntity()
        e2 = OtherEntity()
        e2.id = e1.id
        assert not (e1 == e2)


class TestBaseEntityHash:
    def test_hash_based_on_id(self):
        e1 = ConcreteEntity()
        e2 = ConcreteEntity()
        e2.id = e1.id
        assert hash(e1) == hash(e2)
        assert hash(e1) == hash(e1.id)

    def test_hash_allows_set_usage(self):
        e1 = ConcreteEntity()
        e2 = ConcreteEntity()
        s = {e1, e2}
        assert len(s) == 2

    def test_set_deduplicates_by_id(self):
        e1 = ConcreteEntity()
        e2 = ConcreteEntity()
        e2.id = e1.id
        s = {e1, e2}
        assert len(s) == 1


class TestBaseEntityTouch:
    def test_touch_updates_updated_at(self):
        e = ConcreteEntity()
        original = e.updated_at
        e._touch()
        assert e.updated_at > original

    def test_touch_does_not_change_created_at(self):
        e = ConcreteEntity()
        original_created = e.created_at
        e._touch()
        assert e.created_at == original_created

    def test_touch_sets_utc_time(self):
        e = ConcreteEntity()
        e._touch()
        assert e.updated_at.tzinfo == UTC

    def test_touch_multiple_times(self):
        e = ConcreteEntity()
        times = []
        for _ in range(5):
            e._touch()
            times.append(e.updated_at)
        for i in range(len(times) - 1):
            assert times[i + 1] >= times[i]

    def test_touch_uses_current_time_not_future(self):
        e = ConcreteEntity()
        before = datetime.now(UTC)
        e._touch()
        after = datetime.now(UTC)
        assert before <= e.updated_at <= after
