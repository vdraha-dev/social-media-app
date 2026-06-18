from datetime import datetime
from uuid import UUID

import pytest
from pytz import UTC

from app.identity.domain.events import UserLoggedIn, UserLoggedOut, UserRegistered
from app.identity.domain.value_objects import UserName
from app.shared.domain.value_objects import Email
from app.shared.utils import uuid_gen


class TestUserRegistered:
    def test_creation(self):
        user_id = uuid_gen()
        username = UserName(value="alice")
        email = Email(value="alice@example.com")
        event = UserRegistered(user_id=user_id, username=username, email=email)
        assert event.user_id == user_id

    def test_event_id_is_uuid(self):
        event = UserRegistered(
            user_id=uuid_gen(),
            username=UserName(value="a"),
            email=Email(value="a@a.com"),
        )
        assert isinstance(event.event_id, UUID)

    def test_occured_at_is_utc_datetime(self):
        event = UserRegistered(
            user_id=uuid_gen(),
            username=UserName(value="a"),
            email=Email(value="a@a.com"),
        )
        assert isinstance(event.occured_at, datetime)
        assert event.occured_at.tzinfo == UTC

    def test_occured_at_close_to_now(self):
        before = datetime.now(UTC)
        event = UserRegistered(
            user_id=uuid_gen(),
            username=UserName(value="a"),
            email=Email(value="a@a.com"),
        )
        after = datetime.now(UTC)
        assert before <= event.occured_at <= after

    def test_unique_event_ids(self):
        e1 = UserRegistered(
            user_id=uuid_gen(),
            username=UserName(value="a"),
            email=Email(value="a@a.com"),
        )
        e2 = UserRegistered(
            user_id=uuid_gen(),
            username=UserName(value="b"),
            email=Email(value="b@b.com"),
        )
        assert e1.event_id != e2.event_id

    def test_user_id_is_uuid(self):
        user_id = uuid_gen()
        event = UserRegistered(
            user_id=user_id,
            username=UserName(value="a"),
            email=Email(value="a@a.com"),
        )
        assert isinstance(event.user_id, UUID)

    def test_user_id_matches(self):
        user_id = uuid_gen()
        event = UserRegistered(
            user_id=user_id,
            username=UserName(value="a"),
            email=Email(value="a@a.com"),
        )
        assert event.user_id == user_id

    def test_stores_username(self):
        username = UserName(value="alice")
        event = UserRegistered(
            user_id=uuid_gen(),
            username=username,
            email=Email(value="a@a.com"),
        )
        assert event.username == username  # pyright: ignore

    def test_stores_email(self):
        email = Email(value="alice@example.com")
        event = UserRegistered(
            user_id=uuid_gen(),
            username=UserName(value="alice"),
            email=email,
        )
        assert event.email == email  # pyright: ignore


class TestUserLoggedIn:
    def test_creation(self):
        user_id = uuid_gen()
        event = UserLoggedIn(user_id=user_id)
        assert event.user_id == user_id

    def test_event_id_is_uuid(self):
        event = UserLoggedIn(user_id=uuid_gen())
        assert isinstance(event.event_id, UUID)

    def test_occured_at_is_utc_datetime(self):
        event = UserLoggedIn(user_id=uuid_gen())
        assert isinstance(event.occured_at, datetime)
        assert event.occured_at.tzinfo == UTC

    def test_unique_event_ids(self):
        e1 = UserLoggedIn(user_id=uuid_gen())
        e2 = UserLoggedIn(user_id=uuid_gen())
        assert e1.event_id != e2.event_id

    def test_event_id_has_no_setter(self):
        event = UserLoggedIn(user_id=uuid_gen())
        with pytest.raises(AttributeError):
            event.event_id = uuid_gen()  # pyright: ignore

    def test_occured_at_has_no_setter(self):
        event = UserLoggedIn(user_id=uuid_gen())
        with pytest.raises(AttributeError):
            event.occured_at = datetime.now(UTC)  # pyright: ignore

    def test_cannot_set_arbitrary_attrs(self):
        event = UserLoggedIn(user_id=uuid_gen())
        with pytest.raises(AttributeError):
            event.foo = "bar"  # pyright: ignore


class TestUserLoggedOut:
    def test_creation(self):
        user_id = uuid_gen()
        event = UserLoggedOut(user_id=user_id)
        assert event.user_id == user_id

    def test_event_id_is_uuid(self):
        event = UserLoggedOut(user_id=uuid_gen())
        assert isinstance(event.event_id, UUID)

    def test_occured_at_is_utc_datetime(self):
        event = UserLoggedOut(user_id=uuid_gen())
        assert isinstance(event.occured_at, datetime)
        assert event.occured_at.tzinfo == UTC

    def test_unique_event_ids(self):
        e1 = UserLoggedOut(user_id=uuid_gen())
        e2 = UserLoggedOut(user_id=uuid_gen())
        assert e1.event_id != e2.event_id

    def test_cannot_set_arbitrary_attrs(self):
        event = UserLoggedOut(user_id=uuid_gen())
        with pytest.raises(AttributeError):
            event.foo = "bar"  # pyright: ignore
