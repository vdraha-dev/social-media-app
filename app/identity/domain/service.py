from abc import ABC, abstractmethod
from uuid import UUID

from app.identity.domain.entities import User


class IUserRepository(ABC):
    @abstractmethod
    async def get_user_by_id(self, user_id: UUID) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def save(self, user: User): ...

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool: ...
