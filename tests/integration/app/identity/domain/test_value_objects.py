from dataclasses import FrozenInstanceError

import pytest

from app.identity.domain.value_objects import (
    HashedPassword,
    Role,
    RoleEnum,
    UserName,
)
from app.shared.domain.base_value_object import BaseValueObject


class TestHashedPassword:
    def test_initializes(self):
        hp = HashedPassword("$argon2id$v=19$hashvalue")
        assert hp.value == "$argon2id$v=19$hashvalue"

    def test_str_returns_value(self):
        hp = HashedPassword("hash")
        assert str(hp) == "hash"

    def test_immutable(self):
        hp = HashedPassword("hash")
        with pytest.raises(FrozenInstanceError):
            hp.value = "new_hash"

    def test_equality(self):
        assert HashedPassword("h1") == HashedPassword("h1")
        assert HashedPassword("h1") != HashedPassword("h2")

    def test_inherits_base_value_object(self):
        assert issubclass(HashedPassword, BaseValueObject)


class TestUserName:
    def test_initializes(self):
        un = UserName("john_doe")
        assert un.value == "john_doe"

    def test_str_returns_value(self):
        assert str(UserName("alice")) == "alice"

    def test_immutable(self):
        un = UserName("john")
        with pytest.raises(FrozenInstanceError):
            un.value = "jane"

    def test_equality(self):
        assert UserName("alice") == UserName("alice")
        assert UserName("alice") != UserName("bob")

    def test_inherits_base_value_object(self):
        assert issubclass(UserName, BaseValueObject)


class TestRoleEnum:
    def test_values(self):
        assert RoleEnum.User == "user"
        assert RoleEnum.Admin == "admin"


class TestRole:
    def test_default_is_user(self):
        role = Role()
        assert role.value == RoleEnum.User
        assert not role.is_admin

    def test_admin_role(self):
        role = Role(RoleEnum.Admin)
        assert role.is_admin

    def test_str(self):
        assert str(Role()) == "user"
        assert str(Role(RoleEnum.Admin)) == "admin"

    def test_immutable(self):
        role = Role()
        with pytest.raises(FrozenInstanceError):
            role.value = RoleEnum.Admin

    def test_equality(self):
        assert Role() == Role()
        assert Role(RoleEnum.Admin) == Role(RoleEnum.Admin)
        assert Role() != Role(RoleEnum.Admin)

    def test_validation_raises_for_invalid_type(self):
        with pytest.raises(ValueError, match="Invalid role type"):
            Role("not_a_role")

    def test_inherits_base_value_object(self):
        assert issubclass(Role, BaseValueObject)
