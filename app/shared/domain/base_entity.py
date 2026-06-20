from datetime import datetime
from uuid import UUID

from pytz import UTC

from app.shared.utils import uuid_gen


class BaseEntity:
    __slots__ = ("_id", "_created_at", "_updated_at")

    def __init__(
        self, id: UUID | None, created_at: datetime | None, updated_at: datetime | None
    ):
        self._id = id if id else uuid_gen()
        self._created_at = created_at if created_at else datetime.now(UTC)
        self._updated_at = updated_at if updated_at else datetime.now(UTC)

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def _touch(self):
        """Update the updated_at timestamp to the current UTC time.
        This is useful for marking an entity as 'touched' or modified.
        """
        self._updated_at = datetime.now(UTC)
