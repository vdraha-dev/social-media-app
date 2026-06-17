from datetime import datetime, timedelta
from uuid import UUID

import jwt
from passlib.context import CryptContext
from pytz import UTC

from app.identity.domain.entities import AccessToken
from app.identity.domain.exceptions import InvalidTokenError, TokenExpiredError
from app.identity.domain.service import IPasswordHasher, ITokenService
from app.identity.domain.value_objects import HashedPassword
from app.shared.config import settings


class PasswordHasher(IPasswordHasher):
    hash_context = CryptContext(schemes=settings.HASH_ALGORITHMS, deprecated="auto")

    def hash(self, raw: str) -> HashedPassword:
        return HashedPassword(value=self.hash_context.hash(raw))

    def verify(self, raw: str, hashed: HashedPassword) -> bool:
        return self.hash_context.verify(raw, hashed.value)


class TokenService(ITokenService):
    def generate(self, user_id: UUID, role: str) -> AccessToken:
        expired_at = datetime.now(UTC) + timedelta(
            hours=settings.ACCESS_TOKEN_TTL_HOURS
        )
        token = jwt.encode(  # pyright: ignore
            {
                "user_id": str(user_id),
                "role": role,
                "exp": expired_at,
                "iat": datetime.now(UTC),
            },
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

        return AccessToken(
            token=token, user_id=user_id, expired_at=expired_at, blacklisted=False
        )

    def decode(self, token: str) -> dict[str, str]:
        try:
            return jwt.decode(  # pyright: ignore
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Token expired") from None
        except jwt.InvalidTokenError:
            raise InvalidTokenError("Invalid token") from None
