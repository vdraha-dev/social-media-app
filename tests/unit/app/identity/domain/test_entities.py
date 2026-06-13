from datetime import datetime, timedelta
from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
from pytz import UTC

from app.identity.domain.entities import AccessToken, User
from app.identity.domain.value_objects import HashedPassword, Role, RoleEnum, UserName
from app.shared.domain.value_objects import Email


@pytest.fixture
def user():
    return User(
        username=UserName("testuser"),
        email=Email("test@example.com"),
        password=HashedPassword("hashed_pass"),
        role=Role(),
    )


@pytest.fixture
def admin_user():
    return User(
        username=UserName("admin"),
        email=Email("admin@example.com"),
        password=HashedPassword("hashed_pass"),
        role=Role(RoleEnum.Admin),
    )


class TestUserCreation:
    def test_initializes_fields(self, user):
        assert user.username == UserName("testuser")
        assert user.email == Email("test@example.com")
        assert user.password == HashedPassword("hashed_pass")
        assert user.role == Role()
        assert user.last_login is None

    def test_auto_generates_id(self, user):
        assert isinstance(user.id, UUID)

    def test_auto_generates_timestamps(self, user):
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    def test_default_role_is_user(self, user):
        assert user.role.value == RoleEnum.User


class TestUserRecordLogin:
    def test_sets_last_login(self, user):
        user.record_login()
        assert isinstance(user.last_login, datetime)
        assert user.last_login.tzinfo == UTC

    def test_updates_updated_at(self, user):
        original = user.updated_at
        user.record_login()
        assert user.updated_at > original


class TestUserPromoteToAdmin:
    def test_promotes_user_to_admin(self, user):
        user.promote_to_admin()
        assert user.role.is_admin

    def test_raises_if_already_admin(self, admin_user):
        with pytest.raises(ValueError, match="already an admin"):
            admin_user.promote_to_admin()

    def test_updates_updated_at(self, user):
        original = user.updated_at
        user.promote_to_admin()
        assert user.updated_at > original


class TestUserChangePassword:
    def test_changes_password(self, user):
        new_pass = HashedPassword("new_hashed")
        user.change_password(new_pass)
        assert user.password == new_pass

    def test_updates_updated_at(self, user):
        original = user.updated_at
        user.change_password(HashedPassword("new_hashed"))
        assert user.updated_at > original


class TestAccessTokenCreation:
    @pytest.fixture
    def token(self):
        return AccessToken(
            token="abc123",
            user_id=uuid4(),
            expired_at=datetime.now(UTC) + timedelta(hours=1),
        )

    def test_initializes_fields(self, token):
        assert token.token == "abc123"
        assert isinstance(token.user_id, UUID)
        assert isinstance(token.expired_at, datetime)
        assert token.blacklisted is False

    def test_auto_generates_id(self, token):
        assert isinstance(token.id, UUID)


class TestAccessTokenBlacklist:
    def test_blacklist_sets_flag(self):
        token = AccessToken(
            token="abc", user_id=uuid4(), expired_at=datetime.now(UTC)
        )
        token.blacklist()
        assert token.blacklisted is True

    def test_blacklist_updates_updated_at(self):
        token = AccessToken(
            token="abc", user_id=uuid4(), expired_at=datetime.now(UTC)
        )
        original = token.updated_at
        token.blacklist()
        assert token.updated_at > original


class TestAccessTokenIsValid:
    def test_valid_when_not_blacklisted_and_not_expired(self):
        token = AccessToken(
            token="abc",
            user_id=uuid4(),
            expired_at=datetime.now(UTC) + timedelta(hours=1),
        )
        assert token.is_valid is True

    def test_invalid_when_blacklisted(self):
        token = AccessToken(
            token="abc",
            user_id=uuid4(),
            expired_at=datetime.now(UTC) + timedelta(hours=1),
            blacklisted=True,
        )
        assert token.is_valid is False

    def test_invalid_when_expired(self):
        token = AccessToken(
            token="abc",
            user_id=uuid4(),
            expired_at=datetime.now(UTC) - timedelta(seconds=1),
        )
        assert token.is_valid is False

    def test_invalid_when_blacklisted_and_expired(self):
        token = AccessToken(
            token="abc",
            user_id=uuid4(),
            expired_at=datetime.now(UTC) - timedelta(seconds=1),
            blacklisted=True,
        )
        assert token.is_valid is False
