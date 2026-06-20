from datetime import datetime, timedelta
from uuid import UUID

import jwt
import pytest
from pytz import UTC

from app.identity.domain.exceptions import InvalidTokenError, TokenExpiredError
from app.identity.domain.value_objects import HashedPassword
from app.identity.infrastructure.security import PasswordHasher, TokenService
from app.shared.config import settings


class TestPasswordHasher:
    def test_hash_returns_hashed_password(self):
        hasher = PasswordHasher()
        result = hasher.hash("my_password")
        assert isinstance(result, HashedPassword)
        assert result.value != "my_password"

    def test_verify_correct_password(self):
        hasher = PasswordHasher()
        hashed = hasher.hash("my_password")
        assert hasher.verify("my_password", hashed) is True

    def test_verify_incorrect_password(self):
        hasher = PasswordHasher()
        hashed = hasher.hash("my_password")
        assert hasher.verify("wrong_password", hashed) is False

    def test_verify_empty_string(self):
        hasher = PasswordHasher()
        hashed = hasher.hash("password")
        assert hasher.verify("", hashed) is False


class TestTokenServiceGenerate:
    def test_generate_returns_access_token_with_user_id(self):
        service = TokenService()
        user_id = UUID("12345678-1234-5678-1234-567812345678")
        token = service.generate(user_id, "user")
        assert token.user_id == user_id

    def test_generate_sets_blacklisted_false(self):
        service = TokenService()
        token = service.generate(UUID("12345678-1234-5678-1234-567812345678"), "user")
        assert token.blacklisted is False

    def test_generate_sets_expired_at_in_future(self):
        service = TokenService()
        before = datetime.now(UTC)
        token = service.generate(UUID("12345678-1234-5678-1234-567812345678"), "user")
        after = datetime.now(UTC) + timedelta(hours=settings.ACCESS_TOKEN_TTL_HOURS)
        assert before <= token.expired_at <= after

    def test_generate_token_contains_user_id(self):
        service = TokenService()
        user_id = UUID("12345678-1234-5678-1234-567812345678")
        token = service.generate(user_id, "user")
        payload = jwt.decode(  # pyright: ignore
            token.token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        assert payload["user_id"] == str(user_id)

    def test_generate_token_contains_role(self):
        service = TokenService()
        token = service.generate(UUID("12345678-1234-5678-1234-567812345678"), "admin")
        payload = jwt.decode(  # pyright: ignore
            token.token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        assert payload["role"] == "admin"


class TestTokenServiceDecode:
    def test_decode_valid_token(self):
        service = TokenService()
        user_id = UUID("12345678-1234-5678-1234-567812345678")
        token = service.generate(user_id, "user")
        payload = service.decode(token.token)
        assert payload["user_id"] == str(user_id)
        assert payload["role"] == "user"

    def test_decode_expired_token_raises(self):
        service = TokenService()
        user_id = UUID("12345678-1234-5678-1234-567812345678")
        expired_token = jwt.encode(  # pyright: ignore
            {
                "user_id": str(user_id),
                "role": "user",
                "exp": datetime.now(UTC) - timedelta(hours=1),
                "iat": datetime.now(UTC) - timedelta(hours=2),
            },
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        with pytest.raises(TokenExpiredError, match="Token expired"):
            service.decode(expired_token)

    def test_decode_wrong_signature_raises(self):
        service = TokenService()
        invalid_token = jwt.encode(  # pyright: ignore
            {"user_id": "test", "role": "user"},
            "x" * 32,
            algorithm=settings.ALGORITHM,
        )
        with pytest.raises(InvalidTokenError, match="Invalid token"):
            service.decode(invalid_token)

    def test_decode_malformed_token_raises(self):
        service = TokenService()
        with pytest.raises(InvalidTokenError, match="Invalid token"):
            service.decode("not.a.token")
