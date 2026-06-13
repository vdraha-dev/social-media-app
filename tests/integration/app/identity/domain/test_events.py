from uuid import uuid4

import pytest

from app.identity.domain.events import UserLogedIn, UserLoggedOut, UserRegistered
from app.shared.events.event_bus import DomainEvent


class TestUserRegistered:
    def test_initializes_with_all_fields(self):
        uid = uuid4()
        event = UserRegistered(user_id=uid, username="alice", email="a@b.com")
        assert event.user_id == uid
        assert event.username == "alice"
        assert event.email == "a@b.com"

    def test_is_domain_event_subclass(self):
        assert issubclass(UserRegistered, DomainEvent)

    def test_is_frozen(self):
        event = UserRegistered(user_id=uuid4(), username="a", email="a@b.com")
        with pytest.raises(AttributeError):
            event.username = "b"

    def test_equality(self):
        uid = uuid4()
        e1 = UserRegistered(user_id=uid, username="a", email="a@b.com")
        e2 = UserRegistered(user_id=uid, username="a", email="a@b.com")
        assert e1 == e2


class TestUserLoggedIn:
    def test_initializes(self):
        uid = uuid4()
        event = UserLogedIn(user_id=uid)
        assert event.user_id == uid

    def test_is_domain_event_subclass(self):
        assert issubclass(UserLogedIn, DomainEvent)

    def test_is_frozen(self):
        event = UserLogedIn(user_id=uuid4())
        with pytest.raises(AttributeError):
            event.user_id = uuid4()


class TestUserLoggedOut:
    def test_initializes(self):
        uid = uuid4()
        event = UserLoggedOut(user_id=uid)
        assert event.user_id == uid

    def test_is_domain_event_subclass(self):
        assert issubclass(UserLoggedOut, DomainEvent)

    def test_is_frozen(self):
        event = UserLoggedOut(user_id=uuid4())
        with pytest.raises(AttributeError):
            event.user_id = uuid4()
