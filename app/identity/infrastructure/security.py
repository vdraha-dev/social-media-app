from passlib.context import CryptContext

from app.identity.domain.service import IPasswordHasher
from app.identity.domain.value_objects import HashedPassword
from app.shared.config import settings


class PasswordHasher(IPasswordHasher):
    hash_context = CryptContext(schemes=settings.HASH_ALGORITHMS, deprecated="auto")

    def hash(self, raw: str) -> HashedPassword:
        return HashedPassword(value=self.hash_context.hash(raw))

    def verify(self, raw: str, hashed: HashedPassword) -> bool:
        return self.hash_context.verify(raw, hashed.value)
