import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.identity.domain.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
    UserAlreadyExistsError,
)
from app.identity.presentation.exception_handlers import register_exception_handlers


@pytest.fixture
def app():
    application = FastAPI()
    register_exception_handlers(application)

    @application.get("/test/token-expired")
    async def raise_token_expired():  # pyright: ignore
        raise TokenExpiredError("Token expired")

    @application.get("/test/invalid-token")
    async def raise_invalid_token():  # pyright: ignore
        raise InvalidTokenError("Invalid token")

    @application.get("/test/user-already-exists")
    async def raise_user_already_exists():  # pyright: ignore
        raise UserAlreadyExistsError("User already exists with this email")

    @application.get("/test/invalid-credentials")
    async def raise_invalid_credentials():  # pyright: ignore
        raise InvalidCredentialsError("Invalid credentials. Wrong email or password.")

    return application


@pytest.fixture
def client(app: FastAPI):
    return TestClient(app)


class TestTokenExpiredHandler:
    def test_returns_403(self, client: TestClient):
        response = client.get("/test/token-expired")
        assert response.status_code == 403

    def test_returns_message(self, client: TestClient):
        response = client.get("/test/token-expired")
        assert response.json() == "Token expired"


class TestInvalidTokenHandler:
    def test_returns_403(self, client: TestClient):
        response = client.get("/test/invalid-token")
        assert response.status_code == 403

    def test_returns_message(self, client: TestClient):
        response = client.get("/test/invalid-token")
        assert response.json() == "Invalid token"


class TestUserAlreadyExistsHandler:
    def test_returns_409(self, client: TestClient):
        response = client.get("/test/user-already-exists")
        assert response.status_code == 409

    def test_returns_message(self, client: TestClient):
        response = client.get("/test/user-already-exists")
        assert response.json() == "User already exists with this email"


class TestInvalidCredentialsHandler:
    def test_returns_401(self, client: TestClient):
        response = client.get("/test/invalid-credentials")
        assert response.status_code == 401

    def test_returns_message(self, client: TestClient):
        response = client.get("/test/invalid-credentials")
        assert response.json() == "Invalid credentials. Wrong email or password."
