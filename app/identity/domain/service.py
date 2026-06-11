from abc import ABC, abstractmethod
from uuid import UUID

from app.identity.domain.entities import AccessToken, User


class IUserRepository(ABC):
    @abstractmethod
    async def get_user_by_id(self, user_id: UUID) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def save(self, user: User): ...

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool: ...


class IAccessTokenRepository(ABC):
    @abstractmethod
    async def get_by_token(self, token: str) -> AccessToken | None: ...

    @abstractmethod
    async def save(self, access_token: AccessToken): ...


class IPasswordHasher(ABC):
    @abstractmethod
    def hash(self, raw: str) -> HashedPassword: ...
    @abstractmethod
    def verify(self, raw: str, hashed: HashedPassword) -> bool: ...


class ITokenService(ABC):
    @abstractmethod
    def generate(self, user_id: UUID, role: str) -> AccessToken: ...
    @abstractmethod
    def decode(self, token: str) -> dict: ...
