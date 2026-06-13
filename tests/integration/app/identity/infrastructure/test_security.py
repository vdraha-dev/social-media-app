from datetime import datetime
from uuid import uuid4

import jwt
import pytest
from pytz import UTC

from app.identity.domain.exceptions import InvalidTokenError, TokenExpiredError
from app.identity.domain.value_objects import HashedPassword
from app.shared.config import settings


class TestPasswordHasher:
    def test_hash_returns_hashed_password(self, password_hasher):
        result = password_hasher.hash("my_secret_pass")
        assert isinstance(result, HashedPassword)
        assert result.value != "my_secret_pass"

    def test_verify_correct_password(self, password_hasher):
        hashed = password_hasher.hash("correct_pass")
        assert password_hasher.verify("correct_pass", hashed)

    def test_verify_wrong_password(self, password_hasher):
        hashed = password_hasher.hash("correct_pass")
        assert not password_hasher.verify("wrong_pass", hashed)

    def test_verify_empty_string(self, password_hasher):
        hashed = password_hasher.hash("pass")
        assert not password_hasher.verify("", hashed)

    def test_hash_produces_different_values(self, password_hasher):
        h1 = password_hasher.hash("same_pass")
        h2 = password_hasher.hash("same_pass")
        assert h1.value != h2.value


class TestTokenServiceGenerate:
    def test_generates_access_token(self, token_service):
        user_id = uuid4()
        token = token_service.generate(user_id, "user")

        assert token.token is not None
        assert token.user_id == user_id
        assert isinstance(token.expired_at, datetime)
        assert not token.blacklisted

    def test_generated_token_has_jwt_format(self, token_service):
        token = token_service.generate(uuid4(), "admin")
        parts = token.token.split(".")
        assert len(parts) == 3

    def test_generated_token_decodeable(self, token_service):
        user_id = uuid4()
        token = token_service.generate(user_id, "user")

        payload = jwt.decode(
            token.token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        assert payload["user_id"] == str(user_id)
        assert payload["role"] == "user"


class TestTokenServiceDecode:
    def test_decode_valid_token(self, token_service):
        user_id = uuid4()
        token = token_service.generate(user_id, "admin")

        payload = token_service.decode(token.token)
        assert payload["user_id"] == str(user_id)
        assert payload["role"] == "admin"

    def test_decode_expired_token_raises(self, token_service):
        expired_token = jwt.encode(
            {"exp": datetime(2020, 1, 1, tzinfo=UTC)},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        with pytest.raises(TokenExpiredError):
            token_service.decode(expired_token)

    def test_decode_invalid_token_raises(self, token_service):
        with pytest.raises(InvalidTokenError):
            token_service.decode("not.a.valid.token")

    def test_decode_malformed_token_raises(self, token_service):
        with pytest.raises(InvalidTokenError):
            token_service.decode("")

    def test_decode_token_with_wrong_secret_raises(self, token_service, secret_key):
        token = jwt.encode(
            {"user_id": str(uuid4())},
            secret_key,
            algorithm="HS256",
        )
        with pytest.raises(InvalidTokenError):
            token_service.decode(token)
