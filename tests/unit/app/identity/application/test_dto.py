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

    @pytest.mark.parametrize("password", ["short", "1234567", "", "a" * 7])
    def test_password_too_short(self, password):
        with pytest.raises(ValidationError) as exc:
            RegisterUserRequest(
                username="johndoe",
                email="john@example.com",
                password=password,
            )
        assert "at least 8" in str(exc.value)

    @pytest.mark.parametrize("username", ["ab", "a", "", "12"])
    def test_username_too_short(self, username):
        with pytest.raises(ValidationError) as exc:
            RegisterUserRequest(
                username=username,
                email="john@example.com",
                password="strongpass123",
            )
        assert "at least 3" in str(exc.value)

    def test_exactly_8_char_password(self):
        req = RegisterUserRequest(
            username="johndoe",
            email="john@example.com",
            password="12345678",
        )
        assert req.password == "12345678"

    def test_exactly_3_char_username(self):
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


class TestLoginRequest:
    def test_valid_request(self):
        req = LoginRequest(email="a@b.com", password="secret")
        assert req.email == "a@b.com"
        assert req.password == "secret"

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="not-email", password="secret")


class TestTokenResponse:
    def test_initializes(self):
        resp = TokenResponse(access_token="jwt.token.here", token_type="Bearer")
        assert resp.access_token == "jwt.token.here"
        assert resp.token_type == "Bearer"
