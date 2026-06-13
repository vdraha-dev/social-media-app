from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

import pytest
from pytz import UTC

from app.shared.domain.base_entity import BaseEntity


@dataclass(slots=True)
class ConcreteEntity(BaseEntity):
    name: str = ""


class TestBaseEntityCreation:
    def test_auto_generates_id(self):
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

    def test_unique_ids_across_instances(self):
        e1 = ConcreteEntity()
        e2 = ConcreteEntity()
        assert e1.id != e2.id

    def test_created_at_and_updated_at_are_datetimes(self):
        e = ConcreteEntity()
        assert isinstance(e.created_at, datetime)
        assert isinstance(e.updated_at, datetime)

    def test_timezone_is_utc(self):
        e = ConcreteEntity()
        assert e.created_at.tzinfo == UTC
        assert e.updated_at.tzinfo == UTC


class TestBaseEntityEquality:
    def test_eq_uses_id_when_called_directly(self):
        e1 = ConcreteEntity()
        e2 = ConcreteEntity()
        object.__setattr__(e2, "id", e1.id)
        assert BaseEntity.__eq__(e1, e2)

    def test_not_equal_when_different_id(self):
        e1 = ConcreteEntity()
        e2 = ConcreteEntity()
        assert e1 != e2

    def test_not_equal_when_different_class(self):
        e = ConcreteEntity()
        assert e != "not-an-entity"
        assert e != 42
        assert e != None

    def test_hash_is_none_on_subclass(self):
        e = ConcreteEntity()
        assert ConcreteEntity.__hash__ is None or hash(e) == hash(e.id)


class TestBaseEntityTouch:
    def test_updates_updated_at(self):
        e = ConcreteEntity()
        original = e.updated_at
        e._touch()
        assert e.updated_at > original

    def test_does_not_change_created_at(self):
        e = ConcreteEntity()
        original = e.created_at
        e._touch()
        assert e.created_at == original

    def test_sets_timezone_to_utc_after_touch(self):
        e = ConcreteEntity()
        e._touch()
        assert e.updated_at.tzinfo == UTC
