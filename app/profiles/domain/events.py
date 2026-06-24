from uuid import UUID

from app.shared.domain.event_bus import DomainEvent


class UserProfileCreated(DomainEvent):
    __slots__ = ("_user_id", "_profile_id")

    def __init__(self, user_id: UUID, profile_id: UUID):
        super().__init__()
        self._user_id = user_id
        self._profile_id = profile_id

    @property
    def user_id(self) -> UUID:
        return self._user_id

    @property
    def profile_id(self) -> UUID:
        return self._profile_id
