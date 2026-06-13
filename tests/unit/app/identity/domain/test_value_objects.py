import pytest

from app.identity.domain.value_objects import (
    HashedPassword,
    Role,
    RoleEnum,
    UserName,
)


class TestHashedPassword:
    def test_initializes(self):
        hp = HashedPassword("$2b$12$abc123")
        assert hp.value == "$2b$12$abc123"

    def test_str(self):
        hp = HashedPassword("secret_hash")
        assert str(hp) == "secret_hash"

    def test_immutable(self):
        hp = HashedPassword("hash")
        with pytest.raises(AttributeError):
            hp.value = "new_hash"

    def test_equality(self):
        h1 = HashedPassword("hash")
        h2 = HashedPassword("hash")
        assert h1 == h2

    def test_inequality(self):
        h1 = HashedPassword("hash1")
        h2 = HashedPassword("hash2")
        assert h1 != h2

    def test_validation_not_auto_called(self):
        hp = HashedPassword("")
        assert hp.value == ""


class TestUserName:
    def test_initializes(self):
        un = UserName("john_doe")
        assert un.value == "john_doe"

    def test_str(self):
        un = UserName("john_doe")
        assert str(un) == "john_doe"

    def test_immutable(self):
        un = UserName("john")
        with pytest.raises(AttributeError):
            un.value = "jane"

    def test_equality(self):
        u1 = UserName("alice")
        u2 = UserName("alice")
        assert u1 == u2


class TestRoleEnum:
    def test_user_value(self):
        assert RoleEnum.User == "user"

    def test_admin_value(self):
        assert RoleEnum.Admin == "admin"


class TestRole:
    def test_default_role_is_user(self):
        role = Role()
        assert role.value == RoleEnum.User

    def test_custom_role(self):
        role = Role(RoleEnum.Admin)
        assert role.value == RoleEnum.Admin

    def test_is_admin_false_for_user(self):
        role = Role()
        assert role.is_admin is False

    def test_is_admin_true_for_admin(self):
        role = Role(RoleEnum.Admin)
        assert role.is_admin is True

    def test_str_for_user(self):
        assert str(Role()) == "user"

    def test_str_for_admin(self):
        assert str(Role(RoleEnum.Admin)) == "admin"

    def test_immutable(self):
        role = Role()
        with pytest.raises(AttributeError):
            role.value = RoleEnum.Admin

    def test_equality(self):
        r1 = Role()
        r2 = Role()
        assert r1 == r2

    def test_validate_raises_on_call_with_invalid(self):
        with pytest.raises(ValueError, match="Invalid role type"):
            Role("invalid")
