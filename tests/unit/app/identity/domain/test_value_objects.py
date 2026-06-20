from dataclasses import FrozenInstanceError

import pytest

from app.identity.domain.value_objects import HashedPassword, Role, RoleEnum, UserName


class TestHashedPassword:
    def test_create_valid(self):
        hashed = HashedPassword(value="$argon2id$v=19$m=65536,t=3,p=4$hash")
        assert hashed.value == "$argon2id$v=19$m=65536,t=3,p=4$hash"

    def test_str_returns_value(self):
        hashed = HashedPassword(value="my_hash")
        assert str(hashed) == "my_hash"

    def test_frozen(self):
        hashed = HashedPassword(value="hash")
        with pytest.raises(FrozenInstanceError):
            hashed.value = "new"  # pyright: ignore

    def test_empty_value_raise(self):
        with pytest.raises(ValueError, match="Password cannot be empty"):
            HashedPassword(value="")


class TestUserName:
    def test_create_valid(self):
        name = UserName(value="alice")
        assert name.value == "alice"

    def test_str_returns_value(self):
        name = UserName(value="bob")
        assert str(name) == "bob"

    def test_frozen(self):
        name = UserName(value="alice")
        with pytest.raises(FrozenInstanceError):
            name.value = "bob"  # pyright: ignore

    def test_empty_value_raise(self):
        with pytest.raises(ValueError, match="Username cannot be empty"):
            UserName(value="")


class TestRoleEnum:
    def test_user_value(self):
        assert RoleEnum.User == "user"

    def test_admin_value(self):
        assert RoleEnum.Admin == "admin"

    def test_members(self):
        assert list(RoleEnum) == [RoleEnum.User, RoleEnum.Admin]


class TestRole:
    def test_default_value_is_user(self):
        role = Role()
        assert role.value == RoleEnum.User

    def test_create_admin(self):
        role = Role(value=RoleEnum.Admin)
        assert role.value == RoleEnum.Admin

    def test_is_admin_true_for_admin(self):
        role = Role(value=RoleEnum.Admin)
        assert role.is_admin is True

    def test_is_admin_false_for_user(self):
        role = Role()
        assert role.is_admin is False

    def test_str_for_user(self):
        role = Role()
        assert str(role) == "user"

    def test_str_for_admin(self):
        role = Role(value=RoleEnum.Admin)
        assert str(role) == "admin"

    def test_frozen(self):
        role = Role()
        with pytest.raises(FrozenInstanceError):
            role.value = RoleEnum.Admin  # pyright: ignore
