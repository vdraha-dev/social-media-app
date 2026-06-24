from typing import cast
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.identity.application.dto import TokenResponse, UserResponse
from app.identity.domain.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from app.identity.presentation.dependencies import get_current_user_token
from app.identity.presentation.exception_handlers import (
    register_exception_handlers,
)
from app.identity.presentation.router import auth
from app.shared.infrastructure.database import UnitOfWork, get_uow
from app.shared.utils import uuid_gen


@pytest.fixture
def mock_uow() -> Mock:
    uow = MagicMock(spec=UnitOfWork)
    uow.session = MagicMock()
    return uow


@pytest.fixture
def app(mock_uow: Mock) -> FastAPI:
    app = FastAPI()
    app.include_router(auth)
    register_exception_handlers(app)
    app.dependency_overrides[get_uow] = lambda: cast(UnitOfWork, mock_uow)
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


class TestRegisterEndpoint:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_use_case = MagicMock()
        self.mock_use_case.execute = AsyncMock()
        self._patcher = patch(
            "app.identity.presentation.router.RegisterUserUseCase",
        )
        self.mock_class = self._patcher.start()
        self.mock_class.return_value = self.mock_use_case
        yield
        self._patcher.stop()

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
    def setup(self):
        self.mock_use_case = MagicMock()
        self.mock_use_case.execute = AsyncMock()
        self._patcher = patch(
            "app.identity.presentation.router.LoginUseCase",
        )
        self.mock_class = self._patcher.start()
        self.mock_class.return_value = self.mock_use_case
        yield
        self._patcher.stop()

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

        self.mock_auth_use_case = MagicMock()
        self.mock_auth_use_case.execute = AsyncMock()
        self.mock_logout_use_case = MagicMock()
        self.mock_logout_use_case.execute = AsyncMock()

        self._patcher_auth = patch(
            "app.identity.presentation.router.AuthenticateUserByTokenUseCase",
        )
        self.mock_auth_class = self._patcher_auth.start()
        self.mock_auth_class.return_value = self.mock_auth_use_case

        self._patcher_logout = patch(
            "app.identity.presentation.router.LogoutUseCase",
        )
        self.mock_logout_class = self._patcher_logout.start()
        self.mock_logout_class.return_value = self.mock_logout_use_case

        app.dependency_overrides[get_current_user_token] = lambda: self.mock_token
        yield
        self._patcher_auth.stop()
        self._patcher_logout.stop()
        app.dependency_overrides.pop(get_current_user_token, None)

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

        self.mock_auth_use_case = MagicMock()
        self.mock_auth_use_case.execute = AsyncMock()

        self.mock_user_info_use_case = MagicMock()
        self.mock_user_info_use_case.execute = AsyncMock()

        self._patcher_auth = patch(
            "app.identity.presentation.router.AuthenticateUserByTokenUseCase",
        )
        self.mock_auth_class = self._patcher_auth.start()
        self.mock_auth_class.return_value = self.mock_auth_use_case

        self._patcher_info = patch(
            "app.identity.presentation.router.GetUserInfoByTokenUseCase",
        )
        self.mock_info_class = self._patcher_info.start()
        self.mock_info_class.return_value = self.mock_user_info_use_case

        app.dependency_overrides[get_current_user_token] = lambda: self.mock_token
        yield
        self._patcher_auth.stop()
        self._patcher_info.stop()
        app.dependency_overrides.pop(get_current_user_token, None)

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
