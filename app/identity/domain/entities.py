from dataclasses import dataclass
from datetime import datetime

from pytz import UTC

from app.identity.domain.value_objects import HashedPassword, Role, RoleEnum
from app.shared.domain.base_entity import BaseEntity


@dataclass(slots=True)
class User(BaseEntity):
    username: str
    email: str
    password: HashedPassword
    role: Role
    last_login: datetime | None = None

    def record_login(self):
        self.last_login = datetime.now(UTC)
        self._touch()

    def promote_to_admin(self):
        if self.role.is_admin:
            raise ValueError("User is already an admin.")
        self.role = Role(RoleEnum.Admin)
        self._touch()

    def change_password(self, new_password: HashedPassword):
        self.password = new_password
        self._touch()