from abc import ABC, abstractmethod
from uuid import UUID

from app.profiles.domain.entities import UserProfile


class IProfileRepository(ABC):
    @abstractmethod
    async def save(self, profile: UserProfile): ...

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> UserProfile | None: ...
