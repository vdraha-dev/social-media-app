from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from pytz import UTC


@dataclass(slots=True)
class BaseEntity:
    id: UUID = field(default_factory=uuid4, init=False)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC), init=False)
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC), init=False)

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
        self.updated_at = datetime.now(UTC)
