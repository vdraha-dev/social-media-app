

from abc import ABC, abstractmethod
from uuid import UUID

from app.identity.domain.entities import User
from app.profiles.domain.entities import UserProfile


class IProfileRepository(ABC):
    @abstractmethod
    def save(self, profile: UserProfile): ...
    
    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> UserProfile: ...