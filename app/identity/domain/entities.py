from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from pytz import UTC

from app.identity.domain.value_objects import HashedPassword, Role, RoleEnum, UserName
from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects import Email


class User(BaseEntity):
    __slots__ = ("_username", "_email", "_password", "_role", "_last_login")

    def __init__(
        self,
        username: UserName,
        email: Email,
        password: HashedPassword,
        role: Role,
        last_login: datetime | None = None,
        *,
        id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        super().__init__(id, created_at, updated_at)
        self._username = username
        self._email = email
        self._password = password
        self._role = role
        self._last_login = last_login

    @property
    def username(self) -> UserName:
        return self._username

    @property
    def email(self) -> Email:
        return self._email

    @property
    def password(self) -> HashedPassword:
        return self._password

    @property
    def role(self) -> Role:
        return self._role

    @property
    def last_login(self) -> datetime | None:
        return self._last_login

    def change_username(self, username: UserName):
        if self.username == username:
            return

        self._username = username
        self._touch()

    def cheange_email(self, email: Email):
        if email == self.email:
            return

        self._email = email
        self._touch()

    def change_password(self, new_password: HashedPassword):
        if self.password == new_password:
            return

        self._password = new_password
        self._touch()

    def promote_to_admin(self):
        if self.role.is_admin:
            raise ValueError("User is already an admin.")

        self._role = Role(RoleEnum.Admin)
        self._touch()

    def record_login(self):
        self._last_login = datetime.now(UTC)
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
