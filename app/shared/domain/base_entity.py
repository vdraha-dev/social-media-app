from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from pytz import UTC

from app.shared.domain.value_objects import Id


@dataclass(slots=True)
class BaseEntity:
    id: Id = field(default_factory=lambda: Id(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

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
