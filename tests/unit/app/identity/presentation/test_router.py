from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.identity.presentation.router import auth


@pytest.fixture
def app():
    application = FastAPI()
    application.include_router(auth)
    return application


@pytest.fixture
def client(app):
    return TestClient(app)


class TestRegisterEndpoint:
    def test_register_success(self, client):
        with (
            patch(
                "app.identity.presentation.router.RegisterUserhandler",
            ) as mock_handler_cls,
            patch(
                "app.identity.presentation.router.get_uow",
            ),
        ):
            mock_handler = AsyncMock()
            mock_handler.handle = AsyncMock(
                return_value=MagicMock(
                    id=uuid4(),
                    username="newuser",
                    email="new@example.com",
                    role="user",
                )
            )
            mock_handler_cls.return_value = mock_handler

            response = client.post(
                "/auth/register",
                json={
                    "username": "newuser",
                    "email": "new@example.com",
                    "password": "strongpass123",
                },
            )

            assert response.status_code in (200, 201)

    def test_register_validation_error(self, client):
        response = client.post(
            "/auth/register",
            json={"username": "ab", "email": "bad", "password": "short"},
        )
        assert response.status_code == 422


class TestLoginEndpoint:
    def test_login_success(self, client):
        with (
            patch(
                "app.identity.presentation.router.LoginHandler",
            ) as mock_handler_cls,
            patch(
                "app.identity.presentation.router.get_uow",
            ),
        ):
            mock_handler = AsyncMock()
            mock_handler.handle = AsyncMock(
                return_value=MagicMock(
                    access_token="jwt.token.here",
                    token_type="Bearer",
                )
            )
            mock_handler_cls.return_value = mock_handler

            response = client.post(
                "/auth/login",
                json={"email": "a@b.com", "password": "secret123"},
            )

            assert response.status_code == 200

    def test_login_validation_error(self, client):
        response = client.post(
            "/auth/login",
            json={"email": "not-email", "password": ""},
        )
        assert response.status_code == 422


class TestLogoutEndpoint:
    def test_logout_without_token_returns_401(self, client):
        response = client.post("/auth/logout")
        assert response.status_code == 401

    def test_logout_with_token_calls_handlers(self, client):
        with (
            patch(
                "app.identity.presentation.router.VerifyUserByTokenHandler",
            ) as mock_verify_cls,
            patch(
                "app.identity.presentation.router.LogoutHandler",
            ) as mock_logout_cls,
            patch(
                "app.identity.presentation.router.get_uow",
            ),
        ):
            mock_verify = AsyncMock()
            mock_user = MagicMock()
            mock_user.id = uuid4()
            mock_verify.handle = AsyncMock(return_value=mock_user)
            mock_verify_cls.return_value = mock_verify

            mock_logout = AsyncMock()
            mock_logout.handle = AsyncMock()
            mock_logout_cls.return_value = mock_logout

            response = client.post(
                "/auth/logout",
                headers={"Authorization": "Bearer test_token"},
            )

            assert response.status_code == 204


class TestMeEndpoint:
    def test_get_me_without_token_returns_401(self, client):
        response = client.get("/auth/me")
        assert response.status_code == 401

    def test_get_me_with_token(self, client):
        user_id = uuid4()
        with (
            patch(
                "app.identity.presentation.router.VerifyUserByTokenHandler",
            ) as mock_verify_cls,
            patch(
                "app.identity.presentation.router.get_uow",
            ),
        ):
            mock_verify = AsyncMock()
            mock_user = MagicMock()
            mock_user.id = user_id
            mock_user.username = "testuser"
            mock_user.email = "test@example.com"
            mock_user.role.value = "user"
            mock_verify.handle = AsyncMock(return_value=mock_user)
            mock_verify_cls.return_value = mock_verify

            response = client.get(
                "/auth/me",
                headers={"Authorization": "Bearer valid_token"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["username"] == "testuser"
            assert data["email"] == "test@example.com"
            assert data["role"] == "user"
