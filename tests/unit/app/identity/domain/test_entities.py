from datetime import datetime, timedelta
from uuid import UUID

import pytest
from pytz import UTC

from app.identity.domain.entities import AccessToken, User
from app.identity.domain.value_objects import HashedPassword, Role, RoleEnum, UserName
from app.shared.domain.value_objects import Email
from app.shared.utils import uuid_gen


class TestUserCreation:
    def test_create_with_all_fields(self):
        uid = uuid_gen()
        now = datetime.now(UTC)
        user = User(
            username=UserName(value="alice"),
            email=Email(value="alice@example.com"),
            password=HashedPassword(value="hash"),
            role=Role(),
            last_login=now,
            id=uid,
            created_at=now,
            updated_at=now,
        )
        assert user.id == uid
        assert user.created_at == now
        assert user.updated_at == now
        assert user.last_login == now

    def test_auto_generates_defaults(self):
        user = User(
            username=UserName(value="bob"),
            email=Email(value="bob@example.com"),
            password=HashedPassword(value="hash"),
            role=Role(),
        )
        assert isinstance(user.id, UUID)
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
        assert user.last_login is None

    def test_timezone_is_utc(self):
        user = User(
            username=UserName(value="bob"),
            email=Email(value="bob@example.com"),
            password=HashedPassword(value="hash"),
            role=Role(),
        )
        assert user.created_at.tzinfo == UTC
        assert user.updated_at.tzinfo == UTC


class TestUserProperties:
    def test_username(self):
        name = UserName(value="alice")
        user = User(
            username=name,
            email=Email(value="a@a.com"),
            password=HashedPassword(value="h"),
            role=Role(),
        )
        assert user.username == name

    def test_email(self):
        email = Email(value="a@a.com")
        user = User(
            username=UserName(value="alice"),
            email=email,
            password=HashedPassword(value="h"),
            role=Role(),
        )
        assert user.email == email

    def test_password(self):
        pwd = HashedPassword(value="hash")
        user = User(
            username=UserName(value="alice"),
            email=Email(value="a@a.com"),
            password=pwd,
            role=Role(),
        )
        assert user.password == pwd

    def test_role(self):
        role = Role(RoleEnum.Admin)
        user = User(
            username=UserName(value="alice"),
            email=Email(value="a@a.com"),
            password=HashedPassword(value="h"),
            role=role,
        )
        assert user.role == role

    def test_default_role_is_user(self):
        user = User(
            username=UserName(value="alice"),
            email=Email(value="a@a.com"),
            password=HashedPassword(value="h"),
            role=Role(),
        )
        assert user.role.value == RoleEnum.User


class TestUserChangeUsername:
    def test_changes_username(self):
        user = User(
            username=UserName(value="old"),
            email=Email(value="a@a.com"),
            password=HashedPassword(value="h"),
            role=Role(),
        )
        new = UserName(value="new")
        user.change_username(new)
        assert user.username == new

    def test_touches_on_change(self):
        user = User(
            username=UserName(value="old"),
            email=Email(value="a@a.com"),
            password=HashedPassword(value="h"),
            role=Role(),
        )
        before = user.updated_at
        user.change_username(UserName(value="new"))
        assert user.updated_at > before

    def test_noop_when_same(self):
        name = UserName(value="same")
        user = User(
            username=name,
            email=Email(value="a@a.com"),
            password=HashedPassword(value="h"),
            role=Role(),
        )
        before = user.updated_at
        user.change_username(name)
        assert user.updated_at == before


class TestUserChangeEmail:
    def test_changes_email(self):
        user = User(
            username=UserName(value="u"),
            email=Email(value="old@a.com"),
            password=HashedPassword(value="h"),
            role=Role(),
        )
        new = Email(value="new@a.com")
        user.change_email(new)
        assert user.email == new

    def test_touches_on_change(self):
        user = User(
            username=UserName(value="u"),
            email=Email(value="old@a.com"),
            password=HashedPassword(value="h"),
            role=Role(),
        )
        before = user.updated_at
        user.change_email(Email(value="new@a.com"))
        assert user.updated_at > before

    def test_noop_when_same(self):
        email = Email(value="a@a.com")
        user = User(
            username=UserName(value="u"),
            email=email,
            password=HashedPassword(value="h"),
            role=Role(),
        )
        before = user.updated_at
        user.change_email(email)
        assert user.updated_at == before


class TestUserChangePassword:
    def test_changes_password(self):
        user = User(
            username=UserName(value="u"),
            email=Email(value="a@a.com"),
            password=HashedPassword(value="old"),
            role=Role(),
        )
        new = HashedPassword(value="new")
        user.change_password(new)
        assert user.password == new

    def test_touches_on_change(self):
        user = User(
            username=UserName(value="u"),
            email=Email(value="a@a.com"),
            password=HashedPassword(value="old"),
            role=Role(),
        )
        before = user.updated_at
        user.change_password(HashedPassword(value="new"))
        assert user.updated_at > before

    def test_noop_when_same(self):
        pwd = HashedPassword(value="same")
        user = User(
            username=UserName(value="u"),
            email=Email(value="a@a.com"),
            password=pwd,
            role=Role(),
        )
        before = user.updated_at
        user.change_password(pwd)
        assert user.updated_at == before


class TestUserPromoteToAdmin:
    def test_promotes_user(self):
        user = User(
            username=UserName(value="u"),
            email=Email(value="a@a.com"),
            password=HashedPassword(value="h"),
            role=Role(),
        )
        user.promote_to_admin()
        assert user.role.is_admin

    def test_touches_on_promote(self):
        user = User(
            username=UserName(value="u"),
            email=Email(value="a@a.com"),
            password=HashedPassword(value="h"),
            role=Role(),
        )
        before = user.updated_at
        user.promote_to_admin()
        assert user.updated_at > before

    def test_raises_when_already_admin(self):
        user = User(
            username=UserName(value="u"),
            email=Email(value="a@a.com"),
            password=HashedPassword(value="h"),
            role=Role(RoleEnum.Admin),
        )
        with pytest.raises(ValueError, match="already an admin"):
            user.promote_to_admin()


class TestUserRecordLogin:
    def test_sets_last_login(self):
        user = User(
            username=UserName(value="u"),
            email=Email(value="a@a.com"),
            password=HashedPassword(value="h"),
            role=Role(),
        )
        assert user.last_login is None
        user.record_login()
        assert isinstance(user.last_login, datetime)
        assert user.last_login.tzinfo == UTC

    def test_touches_on_record_login(self):
        user = User(
            username=UserName(value="u"),
            email=Email(value="a@a.com"),
            password=HashedPassword(value="h"),
            role=Role(),
        )
        before = user.updated_at
        user.record_login()
        assert user.updated_at > before


class TestUserEquality:
    def test_same_id_are_equal(self):
        uid = uuid_gen()
        u1 = User(
            username=UserName(value="a"),
            email=Email(value="a@a.com"),
            password=HashedPassword(value="h1"),
            role=Role(),
            id=uid,
        )
        u2 = User(
            username=UserName(value="b"),
            email=Email(value="b@b.com"),
            password=HashedPassword(value="h2"),
            role=Role(),
            id=uid,
        )
        assert u1 == u2

    def test_different_ids_not_equal(self):
        u1 = User(
            username=UserName(value="a"),
            email=Email(value="a@a.com"),
            password=HashedPassword(value="h1"),
            role=Role(),
        )
        u2 = User(
            username=UserName(value="a"),
            email=Email(value="a@a.com"),
            password=HashedPassword(value="h1"),
            role=Role(),
        )
        assert u1 != u2

    def test_not_equal_to_non_user(self):
        user = User(
            username=UserName(value="a"),
            email=Email(value="a@a.com"),
            password=HashedPassword(value="h"),
            role=Role(),
        )
        assert user != "not a user"
        assert user != 42

    def test_not_equal_to_different_entity_subclass(self):
        from app.shared.domain.base_entity import BaseEntity

        class OtherEntity(BaseEntity):
            pass

        uid = uuid_gen()
        user = User(
            username=UserName(value="a"),
            email=Email(value="a@a.com"),
            password=HashedPassword(value="h"),
            role=Role(),
            id=uid,
        )
        other = OtherEntity(uid, None, None)
        assert user != other


class TestUserHash:
    def test_hash_equals_hash_of_id(self):
        user = User(
            username=UserName(value="a"),
            email=Email(value="a@a.com"),
            password=HashedPassword(value="h"),
            role=Role(),
        )
        assert hash(user) == hash(user.id)

    def test_set_deduplicates_by_id(self):
        uid = uuid_gen()
        u1 = User(
            username=UserName(value="a"),
            email=Email(value="a@a.com"),
            password=HashedPassword(value="h"),
            role=Role(),
            id=uid,
        )
        u2 = User(
            username=UserName(value="b"),
            email=Email(value="b@b.com"),
            password=HashedPassword(value="h2"),
            role=Role(),
            id=uid,
        )
        assert len({u1, u2}) == 1


class TestAccessTokenCreation:
    def test_create_with_all_fields(self):
        uid = uuid_gen()
        now = datetime.now(UTC)
        token = AccessToken(
            token="abc",
            user_id=uid,
            expired_at=now + timedelta(hours=1),
            blacklisted=False,
            id=uid,
            created_at=now,
            updated_at=now,
        )
        assert token.token == "abc"
        assert token.user_id == uid
        assert token.expired_at == now + timedelta(hours=1)
        assert token.blacklisted is False
        assert token.id == uid
        assert token.created_at == now
        assert token.updated_at == now

    def test_default_blacklisted_is_false(self):
        token = AccessToken(
            token="abc",
            user_id=uuid_gen(),
            expired_at=datetime.now(UTC) + timedelta(hours=1),
        )
        assert token.blacklisted is False

    def test_auto_generates_id_and_timestamps(self):
        token = AccessToken(
            token="abc",
            user_id=uuid_gen(),
            expired_at=datetime.now(UTC) + timedelta(hours=1),
        )
        assert isinstance(token.id, UUID)
        assert isinstance(token.created_at, datetime)
        assert isinstance(token.updated_at, datetime)

    def test_timezone_is_utc(self):
        token = AccessToken(
            token="abc",
            user_id=uuid_gen(),
            expired_at=datetime.now(UTC) + timedelta(hours=1),
        )
        assert token.created_at.tzinfo == UTC
        assert token.updated_at.tzinfo == UTC


class TestAccessTokenBlacklist:
    def test_blacklist_sets_true(self):
        token = AccessToken(
            token="abc",
            user_id=uuid_gen(),
            expired_at=datetime.now(UTC) + timedelta(hours=1),
        )
        token.blacklist()
        assert token.blacklisted is True

    def test_touches_on_blacklist(self):
        token = AccessToken(
            token="abc",
            user_id=uuid_gen(),
            expired_at=datetime.now(UTC) + timedelta(hours=1),
        )
        before = token.updated_at
        token.blacklist()
        assert token.updated_at > before

    def test_noop_when_already_blacklisted(self):
        token = AccessToken(
            token="abc",
            user_id=uuid_gen(),
            expired_at=datetime.now(UTC) + timedelta(hours=1),
            blacklisted=True,
        )
        before = token.updated_at
        token.blacklist()
        assert token.updated_at == before


class TestAccessTokenIsValid:
    def test_valid_when_not_blacklisted_and_not_expired(self):
        token = AccessToken(
            token="abc",
            user_id=uuid_gen(),
            expired_at=datetime.now(UTC) + timedelta(hours=1),
        )
        assert token.is_valid is True

    def test_invalid_when_blacklisted(self):
        token = AccessToken(
            token="abc",
            user_id=uuid_gen(),
            expired_at=datetime.now(UTC) + timedelta(hours=1),
            blacklisted=True,
        )
        assert token.is_valid is False

    def test_invalid_when_expired(self):
        token = AccessToken(
            token="abc",
            user_id=uuid_gen(),
            expired_at=datetime.now(UTC) - timedelta(seconds=1),
        )
        assert token.is_valid is False

    def test_invalid_when_blacklisted_and_expired(self):
        token = AccessToken(
            token="abc",
            user_id=uuid_gen(),
            expired_at=datetime.now(UTC) - timedelta(seconds=1),
            blacklisted=True,
        )
        assert token.is_valid is False


class TestAccessTokenEquality:
    def test_same_id_are_equal(self):
        uid = uuid_gen()
        t1 = AccessToken(
            token="a", user_id=uuid_gen(), expired_at=datetime.now(UTC), id=uid
        )
        t2 = AccessToken(
            token="b", user_id=uuid_gen(), expired_at=datetime.now(UTC), id=uid
        )
        assert t1 == t2

    def test_different_ids_not_equal(self):
        t1 = AccessToken(token="a", user_id=uuid_gen(), expired_at=datetime.now(UTC))
        t2 = AccessToken(token="a", user_id=uuid_gen(), expired_at=datetime.now(UTC))
        assert t1 != t2
