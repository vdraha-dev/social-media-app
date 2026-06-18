from dataclasses import dataclass
from enum import StrEnum

from app.shared.domain.base_value_object import BaseValueObject


@dataclass(frozen=True, slots=True)
class HashedPassword(BaseValueObject):
    value: str

    def _validate(self):
        if not self.value:
            raise ValueError("Invalid password. Password cannot be empty.")

    def __str__(self):
        return self.value


@dataclass(frozen=True, slots=True)
class UserName(BaseValueObject):
    value: str

    def _validate(self):
        if not self.value:
            raise ValueError("Invalid username. Username cannot be empty.")

    def __str__(self):
        return self.value


class RoleEnum(StrEnum):
    User = "user"
    Admin = "admin"


@dataclass(frozen=True, slots=True)
class Role(BaseValueObject):
    value: RoleEnum = RoleEnum.User

    def _validate(self): ...

    @property
    def is_admin(self) -> bool:
        return self.value == RoleEnum.Admin

    def __str__(self):
        return str(self.value)
