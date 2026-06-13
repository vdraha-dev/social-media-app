from datetime import datetime
from unittest.mock import patch
from uuid import uuid4

import jwt
import pytest
from pytz import UTC

from app.identity.domain.exceptions import InvalidTokenError, TokenExpiredError
from app.identity.domain.value_objects import HashedPassword
from app.identity.infrastructure.security import PasswordHasher, TokenService


class TestPasswordHasher:
    def test_hash_returns_hashed_password(self):
        hasher = PasswordHasher()
        result = hasher.hash("my_secret_pass")
        assert isinstance(result, HashedPassword)
        assert result.value != "my_secret_pass"

    def test_verify_correct_password(self):
        hasher = PasswordHasher()
        hashed = hasher.hash("correct_pass")
        assert hasher.verify("correct_pass", hashed) is True

    def test_verify_wrong_password(self):
        hasher = PasswordHasher()
        hashed = hasher.hash("correct_pass")
        assert hasher.verify("wrong_pass", hashed) is False

    def test_verify_with_empty_string(self):
        hasher = PasswordHasher()
        hashed = hasher.hash("pass")
        assert hasher.verify("", hashed) is False

    def test_hash_different_each_time(self):
        hasher = PasswordHasher()
        h1 = hasher.hash("same_pass")
        h2 = hasher.hash("same_pass")
        assert h1.value != h2.value


class TestTokenServiceGenerate:
    def test_generates_access_token(self):
        service = TokenService()
        user_id = uuid4()
        token = service.generate(user_id, "user")

        assert token.token is not None
        assert token.user_id == user_id
        assert isinstance(token.expired_at, datetime)
        assert token.blacklisted is False

    def test_generated_token_has_jwt_format(self):
        service = TokenService()
        token = service.generate(uuid4(), "admin")

        parts = token.token.split(".")
        assert len(parts) == 3

    def test_generated_token_is_decodeable(self):
        with patch("app.identity.infrastructure.security.settings") as mock_settings:
            mock_settings.HASH_ALGORITHMS = ["argon2"]
            mock_settings.SECRET_KEY = "change-me-in-production"
            mock_settings.ALGORITHM = "HS256"
            mock_settings.ACCESS_TOKEN_TTL_HOURS = 24
            service = TokenService()

            user_id = uuid4()
            token = service.generate(user_id, "user")

        payload = jwt.decode(
            token.token,
            "change-me-in-production",
            algorithms=["HS256"],
        )
        assert payload["user_id"] == str(user_id)
        assert payload["role"] == "user"


class TestTokenServiceDecode:
    def test_decode_valid_token(self):
        service = TokenService()
        user_id = uuid4()
        token = service.generate(user_id, "admin")

        payload = service.decode(token.token)
        assert payload["user_id"] == str(user_id)
        assert payload["role"] == "admin"

    def test_decode_expired_token_raises(self):
        service = TokenService()
        with patch("app.identity.infrastructure.security.settings") as mock_settings:
            mock_settings.SECRET_KEY = "test-secret"
            mock_settings.ALGORITHM = "HS256"
            expired_token = jwt.encode(
                {"exp": datetime(2020, 1, 1, tzinfo=UTC)},
                "test-secret",
                algorithm="HS256",
            )
            with pytest.raises(TokenExpiredError):
                service.decode(expired_token)

    def test_decode_invalid_token_raises(self):
        service = TokenService()
        with pytest.raises(InvalidTokenError):
            service.decode("not.a.valid.token")

    def test_decode_malformed_token_raises(self):
        service = TokenService()
        with pytest.raises(InvalidTokenError):
            service.decode("")

    def test_decode_token_with_wrong_secret_raises(self):
        service = TokenService()
        token = jwt.encode(
            {"user_id": str(uuid4())},
            "wrong-secret",
            algorithm="HS256",
        )
        with pytest.raises(InvalidTokenError):
            service.decode(token)
