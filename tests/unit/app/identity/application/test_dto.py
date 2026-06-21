from uuid import UUID

import pytest
from pydantic import ValidationError

from app.identity.application.dto import (
    LoginRequest,
    RegisterUserRequest,
    TokenResponse,
    UserResponse,
)


class TestRegisterUserRequest:
    def test_valid(self):
        dto = RegisterUserRequest(
            username="alice",
            email="alice@example.com",
            password="password123",
        )
        assert dto.username == "alice"
        assert dto.email == "alice@example.com"
        assert dto.password == "password123"

    def test_password_too_short(self):
        with pytest.raises(ValidationError, match="at least 8 characters"):
            RegisterUserRequest(
                username="alice",
                email="alice@example.com",
                password="short",
            )

    def test_password_minimum_length(self):
        dto = RegisterUserRequest(
            username="alice",
            email="alice@example.com",
            password="12345678",
        )
        assert dto.password == "12345678"

    def test_username_too_short(self):
        with pytest.raises(ValidationError, match="at least 3 characters"):
            RegisterUserRequest(
                username="ab",
                email="alice@example.com",
                password="password123",
            )

    def test_username_minimum_length(self):
        dto = RegisterUserRequest(
            username="abc",
            email="abc@example.com",
            password="password123",
        )
        assert dto.username == "abc"

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            RegisterUserRequest(
                username="alice",
                email="not-an-email",
                password="password123",
            )

    def test_missing_fields(self):
        with pytest.raises(ValidationError):
            RegisterUserRequest()  # pyright: ignore


class TestUserResponse:
    def test_valid(self):
        uid = UUID("12345678-1234-5678-1234-567812345678")
        dto = UserResponse(
            id=uid,
            username="alice",
            email="alice@example.com",
            role="user",
        )
        assert dto.id == uid
        assert dto.username == "alice"
        assert dto.email == "alice@example.com"
        assert dto.role == "user"

    def test_missing_fields(self):
        with pytest.raises(ValidationError):
            UserResponse()  # pyright: ignore


class TestLoginRequest:
    def test_valid(self):
        dto = LoginRequest(
            email="alice@example.com",
            password="password123",
        )
        assert dto.email == "alice@example.com"
        assert dto.password == "password123"

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            LoginRequest(
                email="not-an-email",
                password="password123",
            )

    def test_missing_fields(self):
        with pytest.raises(ValidationError):
            LoginRequest()  # pyright: ignore


class TestTokenResponse:
    def test_valid(self):
        dto = TokenResponse(
            access_token="eyJ...",
            token_type="bearer",
        )
        assert dto.access_token == "eyJ..."
        assert dto.token_type == "bearer"

    def test_missing_fields(self):
        with pytest.raises(ValidationError):
            TokenResponse()  # pyright: ignore
