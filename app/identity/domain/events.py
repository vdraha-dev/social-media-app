from uuid import UUID

from app.identity.domain.value_objects import UserName
from app.shared.domain.value_objects import Email
from app.shared.domain.event_bus import DomainEvent


class _UserIdMixin(DomainEvent):
    __slots__ = ("_user_id",)

    def __init__(self, user_id: UUID):
        super().__init__()
        self._user_id = user_id

    @property
    def user_id(self) -> UUID:
        return self._user_id


class UserRegistered(_UserIdMixin):
    __slots__ = ("_username", "_email")

    def __init__(self, user_id: UUID, username: UserName, email: Email):
        super().__init__(user_id=user_id)
        self._username = username
        self._email = email

    @property
    def username(self) -> UserName:
        return self._username

    @property
    def email(self) -> Email:
        return self._email


class UserLoggedIn(_UserIdMixin):
    __slots__ = ()


class UserLoggedOut(_UserIdMixin):
    __slots__ = ()
