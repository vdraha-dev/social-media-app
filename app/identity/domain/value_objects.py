import re
from dataclasses import dataclass
from enum import StrEnum


@dataclass(frozen=True, slots=True)
class HashedPassword:
    value: str

    def _validation(self):
        if not self.value:
            raise ValueError("Invalid password. Password cannot be empty.")


@dataclass(frozen=True, slots=True)
class UserName:
    value: str


@dataclass(frozen=True, slots=True)
class Email:
    value: str

    def _validation(self):
        if not re.match(
            r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", self.value
        ):
            raise ValueError(f"Invalid email address: {self.value!r}")


class RoleEnum(StrEnum):
    User = "user"
    Admin = "admin"


@dataclass(frozen=True, slots=True)
class Role:
    value: RoleEnum = RoleEnum.User

    def _validate(self):
        if not isinstance(self.value, RoleEnum):
            raise ValueError(f"Invalid role type: {type(self.value)}")

    @property
    def is_admin(self) -> bool:
        return self.value == RoleEnum.Admin
