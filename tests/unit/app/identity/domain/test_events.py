from uuid import UUID, uuid4

import pytest

from app.identity.domain.events import UserLogedIn, UserLoggedOut, UserRegistered
from app.shared.events.event_bus import DomainEvent


class TestUserRegistered:
    def test_initializes_fields(self):
        user_id = uuid4()
        event = UserRegistered(user_id=user_id, username="alice", email="a@b.com")
        assert event.user_id == user_id
        assert event.username == "alice"
        assert event.email == "a@b.com"

    def test_is_dataclass(self):
        user_id = uuid4()
        e1 = UserRegistered(user_id=user_id, username="a", email="a@b.com")
        e2 = UserRegistered(user_id=user_id, username="a", email="a@b.com")
        assert e1 == e2

    def test_is_domain_event(self):
        assert issubclass(UserRegistered, DomainEvent)

    def test_is_frozen(self):
        event = UserRegistered(user_id=uuid4(), username="a", email="a@b.com")
        with pytest.raises(AttributeError):
            event.username = "b"


class TestUserLogedIn:
    def test_initializes_fields(self):
        user_id = uuid4()
        event = UserLogedIn(user_id=user_id)
        assert event.user_id == user_id

    def test_is_domain_event(self):
        assert issubclass(UserLogedIn, DomainEvent)


class TestUserLoggedOut:
    def test_initializes_fields(self):
        user_id = uuid4()
        event = UserLoggedOut(user_id=user_id)
        assert event.user_id == user_id

    def test_is_domain_event(self):
        assert issubclass(UserLoggedOut, DomainEvent)
