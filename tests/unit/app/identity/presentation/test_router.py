from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.identity.application.dto import TokenResponse, UserResponse
from app.identity.application.use_cases import (
    AuthenticateUserByTokenUseCase,
    GetUserInfoByTokenUseCase,
    LoginUseCase,
    LogoutUseCase,
    RegisterUserUseCase,
)
from app.identity.domain.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from app.identity.presentation.dependencies import get_current_user_token
from app.identity.presentation.exception_handlers import (
    register_exception_handlers,
)
from app.identity.presentation.router import (
    auth,
    auth_user_dependency,
    login_dependency,
    logout_dependency,
    register_dependency,
    user_info_dependency,
)
from app.shared.utils import uuid_gen


@pytest.fixture
def app() -> FastAPI:
    app = FastAPI()
    app.include_router(auth)
    register_exception_handlers(app)
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


class TestRegisterEndpoint:
    @pytest.fixture(autouse=True)
    def setup(self, app: FastAPI):
        self.mock_use_case = MagicMock(spec=RegisterUserUseCase)
        self.mock_use_case.execute = AsyncMock()
        app.dependency_overrides[register_dependency] = lambda: self.mock_use_case
        yield
        app.dependency_overrides.pop(register_dependency, None)

    def test_register_success(self, client: TestClient):
        user_id = uuid_gen()
        self.mock_use_case.execute.return_value = UserResponse(
            id=user_id,
            username="alice",
            email="alice@example.com",
            role="user",
        )

        payload = {
            "username": "alice",
            "email": "alice@example.com",
            "password": "password123",
        }

        response = client.post("/auth/register", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == str(user_id)
        assert data["username"] == "alice"
        assert data["email"] == "alice@example.com"
        assert data["role"] == "user"
        self.mock_use_case.execute.assert_awaited_once()

    def test_register_user_already_exists(self, client: TestClient):
        self.mock_use_case.execute.side_effect = UserAlreadyExistsError(
            "User already exists with this email"
        )

        payload = {
            "username": "alice",
            "email": "alice@example.com",
            "password": "password123",
        }

        response = client.post("/auth/register", json=payload)

        assert response.status_code == 409


class TestLoginEndpoint:
    @pytest.fixture(autouse=True)
    def setup(self, app: FastAPI):
        self.mock_use_case = MagicMock(spec=LoginUseCase)
        self.mock_use_case.execute = AsyncMock()
        app.dependency_overrides[login_dependency] = lambda: self.mock_use_case
        yield
        app.dependency_overrides.pop(login_dependency, None)

    def test_login_success(self, client: TestClient):
        self.mock_use_case.execute.return_value = TokenResponse(
            access_token="jwt_token_abc",
            token_type="Bearer",
        )

        payload = {"email": "alice@example.com", "password": "password123"}

        response = client.post("/auth/login", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "jwt_token_abc"
        assert data["token_type"] == "Bearer"

    def test_login_invalid_credentials(self, client: TestClient):
        self.mock_use_case.execute.side_effect = InvalidCredentialsError(
            "Invalid credentials. Wrong email or password."
        )

        payload = {"email": "wrong@example.com", "password": "wrong"}

        response = client.post("/auth/login", json=payload)

        assert response.status_code == 401


class TestLogoutEndpoint:
    @pytest.fixture(autouse=True)
    def setup(self, app: FastAPI):
        self.mock_token = "valid_token"

        self.mock_auth_use_case = MagicMock(spec=AuthenticateUserByTokenUseCase)
        self.mock_auth_use_case.execute = AsyncMock()
        self.mock_logout_use_case = MagicMock(spec=LogoutUseCase)
        self.mock_logout_use_case.execute = AsyncMock()

        app.dependency_overrides[get_current_user_token] = lambda: self.mock_token
        app.dependency_overrides[auth_user_dependency] = lambda: self.mock_auth_use_case
        app.dependency_overrides[logout_dependency] = lambda: self.mock_logout_use_case
        yield
        app.dependency_overrides.pop(get_current_user_token, None)
        app.dependency_overrides.pop(auth_user_dependency, None)
        app.dependency_overrides.pop(logout_dependency, None)

    def test_logout_success(self, client: TestClient):
        user_id = uuid_gen()
        self.mock_auth_use_case.execute.return_value = user_id

        response = client.post("/auth/logout")

        assert response.status_code == 204
        self.mock_auth_use_case.execute.assert_awaited_once_with(self.mock_token)
        self.mock_logout_use_case.execute.assert_awaited_once_with(user_id)


class TestGetMeEndpoint:
    @pytest.fixture(autouse=True)
    def setup(self, app: FastAPI):
        self.mock_token = "valid_token"

        self.mock_auth_use_case = MagicMock(spec=AuthenticateUserByTokenUseCase)
        self.mock_auth_use_case.execute = AsyncMock()

        self.mock_user_info_use_case = MagicMock(spec=GetUserInfoByTokenUseCase)
        self.mock_user_info_use_case.execute = AsyncMock()

        app.dependency_overrides[get_current_user_token] = lambda: self.mock_token
        app.dependency_overrides[auth_user_dependency] = lambda: self.mock_auth_use_case
        app.dependency_overrides[user_info_dependency] = lambda: (
            self.mock_user_info_use_case
        )
        yield
        app.dependency_overrides.pop(get_current_user_token, None)
        app.dependency_overrides.pop(auth_user_dependency, None)
        app.dependency_overrides.pop(user_info_dependency, None)

    def test_get_me_success(self, client: TestClient):
        user_id = uuid_gen()
        self.mock_auth_use_case.execute.return_value = user_id
        self.mock_user_info_use_case.execute.return_value = UserResponse(
            id=user_id,
            username="alice",
            email="alice@example.com",
            role="user",
        )

        response = client.get("/auth/me")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(user_id)
        assert data["username"] == "alice"
        assert data["email"] == "alice@example.com"
        assert data["role"] == "user"
        self.mock_auth_use_case.execute.assert_awaited_once_with(self.mock_token)

    def test_get_me_invalid_token(self, client: TestClient):
        self.mock_auth_use_case.execute.side_effect = InvalidCredentialsError(
            "Invalid credentials"
        )

        response = client.get("/auth/me")

        assert response.status_code == 401
