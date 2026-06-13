import pytest
from pydantic import ValidationError

from app.identity.application.dto import (
    LoginRequest,
    RegisterUserRequest,
    TokenResponse,
    UserResponse,
)


class TestRegisterUserRequest:
    def test_valid_request(self):
        req = RegisterUserRequest(
            username="johndoe",
            email="john@example.com",
            password="strongpass123",
        )
        assert req.username == "johndoe"
        assert req.email == "john@example.com"
        assert req.password == "strongpass123"

    def test_password_too_short(self):
        with pytest.raises(ValidationError, match="at least 8"):
            RegisterUserRequest(
                username="johndoe",
                email="john@example.com",
                password="short",
            )

    def test_password_exactly_8(self):
        req = RegisterUserRequest(
            username="johndoe",
            email="john@example.com",
            password="12345678",
        )
        assert req.password == "12345678"

    def test_username_too_short(self):
        with pytest.raises(ValidationError, match="at least 3"):
            RegisterUserRequest(
                username="ab",
                email="john@example.com",
                password="strongpass123",
            )

    def test_username_exactly_3(self):
        req = RegisterUserRequest(
            username="abc",
            email="john@example.com",
            password="strongpass123",
        )
        assert req.username == "abc"

    def test_invalid_email_raises(self):
        with pytest.raises(ValidationError):
            RegisterUserRequest(
                username="johndoe",
                email="not-an-email",
                password="strongpass123",
            )


class TestLoginRequest:
    def test_valid_request(self):
        req = LoginRequest(email="a@b.com", password="secret")
        assert req.email == "a@b.com"
        assert req.password == "secret"

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="not-email", password="secret")


class TestUserResponse:
    def test_initializes(self):
        resp = UserResponse(
            id="550e8400-e29b-41d4-a716-446655440000",
            username="alice",
            email="alice@example.com",
            role="user",
        )
        assert resp.username == "alice"
        assert resp.email == "alice@example.com"
        assert resp.role == "user"
        data = resp.model_dump()
        assert data["username"] == "alice"
        assert data["email"] == "alice@example.com"
        assert data["role"] == "user"


class TestTokenResponse:
    def test_initializes(self):
        resp = TokenResponse(access_token="jwt.token.here", token_type="Bearer")
        assert resp.access_token == "jwt.token.here"
        assert resp.token_type == "Bearer"
