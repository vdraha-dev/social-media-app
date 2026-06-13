from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from pytz import UTC

from app.identity.domain.entities import AccessToken, User
from app.identity.domain.value_objects import HashedPassword, Role, RoleEnum, UserName
from app.shared.domain.value_objects import Email


class TestUserEntity:
    def test_creates_user_with_required_fields(self):
        user = User(
            username=UserName("alice"),
            email=Email("alice@example.com"),
            password=HashedPassword("hash"),
            role=Role(),
        )
        assert isinstance(user.id, type(uuid4()))
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
        assert user.last_login is None
        assert user.role.value == RoleEnum.User

    def test_record_login_updates_state(self, sample_user):
        before = sample_user.updated_at
        sample_user.record_login()
        assert sample_user.last_login is not None
        assert sample_user.last_login.tzinfo == UTC
        assert sample_user.updated_at > before

    def test_promote_to_admin_changes_role(self, sample_user):
        sample_user.promote_to_admin()
        assert sample_user.role.is_admin

    def test_promote_to_admin_when_already_admin_raises(self, admin_user):
        with pytest.raises(ValueError, match="already an admin"):
            admin_user.promote_to_admin()

    def test_change_password_updates_password(self, sample_user):
        new_pass = HashedPassword("new_hash_value")
        sample_user.change_password(new_pass)
        assert sample_user.password == new_pass

    def test_change_password_touches_entity(self, sample_user):
        before = sample_user.updated_at
        sample_user.change_password(HashedPassword("new_hash"))
        assert sample_user.updated_at > before

    def test_equality_same_object(self, sample_user):
        assert sample_user == sample_user

    def test_inequality_different_users(self, sample_user):
        other = User(
            username=UserName("other"),
            email=Email("other@b.com"),
            password=HashedPassword("h"),
            role=Role(),
        )
        assert sample_user != other

    def test_string_representations(self, sample_user):
        assert str(sample_user.username) == "testuser"
        assert str(sample_user.email) == "test@example.com"
        assert sample_user.role.is_admin is False


class TestAccessTokenEntity:
    def test_creates_token_with_defaults(self):
        token = AccessToken(
            token="jwt_string",
            user_id=uuid4(),
            expired_at=datetime.now(UTC) + timedelta(hours=1),
        )
        assert not token.blacklisted
        assert isinstance(token.id, type(uuid4()))

    def test_blacklist_sets_flag(self):
        expires = datetime.now(UTC) + timedelta(hours=1)
        token = AccessToken(token="t", user_id=uuid4(), expired_at=expires)
        token.blacklist()
        assert token.blacklisted

    def test_is_valid_when_not_blacklisted_and_not_expired(self):
        token = AccessToken(
            token="t",
            user_id=uuid4(),
            expired_at=datetime.now(UTC) + timedelta(hours=1),
        )
        assert token.is_valid

    def test_is_invalid_when_blacklisted(self):
        token = AccessToken(
            token="t",
            user_id=uuid4(),
            expired_at=datetime.now(UTC) + timedelta(hours=1),
            blacklisted=True,
        )
        assert not token.is_valid

    def test_is_invalid_when_expired(self):
        token = AccessToken(
            token="t",
            user_id=uuid4(),
            expired_at=datetime.now(UTC) - timedelta(seconds=1),
        )
        assert not token.is_valid
