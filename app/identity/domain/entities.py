from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from pytz import UTC

from app.identity.domain.value_objects import HashedPassword, Role, RoleEnum, UserName
from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects import Email


@dataclass(slots=True)
class User(BaseEntity):
    username: UserName
    email: Email
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


@dataclass(slots=True)
class AccessToken(BaseEntity):
    token: str
    user_id: UUID
    expired_at: datetime
    blacklisted: bool = False

    def blacklist(self):
        self.blacklisted = True
        self._touch()

    @property
    def is_valid(self) -> bool:
        return not self.blacklisted and self.expired_at > datetime.now(UTC)
