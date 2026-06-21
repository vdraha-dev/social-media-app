import pytest
from fastapi import FastAPI
from httpx2 import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.identity.presentation.exception_handlers import register_exception_handlers
from app.identity.presentation.router import auth, get_uow
from app.shared.infrastructure.database import UnitOfWork

REGISTER_URL = "/auth/register"
LOGIN_URL = "/auth/login"
LOGOUT_URL = "/auth/logout"
ME_URL = "/auth/me"


@pytest.fixture
def app(session: AsyncSession) -> FastAPI:
    application = FastAPI()
    application.include_router(auth)
    register_exception_handlers(application)

    async def get_test_uow():
        uow = UnitOfWork(session)
        yield uow

    application.dependency_overrides[get_uow] = get_test_uow
    return application


@pytest.fixture
async def client(app: FastAPI):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestRegisterEndpoint:
    async def test_register_success(self, client: AsyncClient):
        payload = {
            "username": "alice",
            "email": "alice@example.com",
            "password": "password123",
        }
        response = await client.post(REGISTER_URL, json=payload)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["username"] == "alice"
        assert data["email"] == "alice@example.com"
        assert data["role"] == "user"

    async def test_register_duplicate_email(self, client: AsyncClient):
        payload = {
            "username": "alice",
            "email": "alice@example.com",
            "password": "password123",
        }
        await client.post(REGISTER_URL, json=payload)
        response = await client.post(REGISTER_URL, json=payload)
        assert response.status_code == 409
        assert response.json() == "User already exists with this email"

    async def test_register_invalid_username_too_short(self, client: AsyncClient):
        payload = {
            "username": "al",
            "email": "alice@example.com",
            "password": "password123",
        }
        response = await client.post(REGISTER_URL, json=payload)
        assert response.status_code == 422

    async def test_register_invalid_password_too_short(self, client: AsyncClient):
        payload = {
            "username": "alice",
            "email": "alice@example.com",
            "password": "short",
        }
        response = await client.post(REGISTER_URL, json=payload)
        assert response.status_code == 422


class TestLoginEndpoint:
    async def test_login_success(self, client: AsyncClient):
        register_payload = {
            "username": "alice",
            "email": "alice@example.com",
            "password": "password123",
        }
        await client.post(REGISTER_URL, json=register_payload)

        login_payload = {
            "email": "alice@example.com",
            "password": "password123",
        }
        response = await client.post(LOGIN_URL, json=login_payload)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "Bearer"

    async def test_login_invalid_email(self, client: AsyncClient):
        login_payload = {
            "email": "nonexistent@example.com",
            "password": "password123",
        }
        response = await client.post(LOGIN_URL, json=login_payload)
        assert response.status_code == 401

    async def test_login_wrong_password(self, client: AsyncClient):
        register_payload = {
            "username": "alice",
            "email": "alice@example.com",
            "password": "password123",
        }
        await client.post(REGISTER_URL, json=register_payload)

        login_payload = {
            "email": "alice@example.com",
            "password": "wrong_password",
        }
        response = await client.post(LOGIN_URL, json=login_payload)
        assert response.status_code == 401


class TestLogoutEndpoint:
    async def test_logout_success(self, client: AsyncClient):
        register_payload = {
            "username": "alice",
            "email": "alice@example.com",
            "password": "password123",
        }
        await client.post(REGISTER_URL, json=register_payload)

        login_payload = {
            "email": "alice@example.com",
            "password": "password123",
        }
        login_response = await client.post(LOGIN_URL, json=login_payload)
        token = login_response.json()["access_token"]

        response = await client.post(
            LOGOUT_URL,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 204

    async def test_logout_unauthorized(self, client: AsyncClient):
        response = await client.post(LOGOUT_URL)
        assert response.status_code == 401


class TestGetMeEndpoint:
    async def test_get_me_success(self, client: AsyncClient):
        register_payload = {
            "username": "alice",
            "email": "alice@example.com",
            "password": "password123",
        }
        await client.post(REGISTER_URL, json=register_payload)

        login_payload = {
            "email": "alice@example.com",
            "password": "password123",
        }
        login_response = await client.post(LOGIN_URL, json=login_payload)
        token = login_response.json()["access_token"]

        response = await client.get(
            ME_URL,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "alice"
        assert data["email"] == "alice@example.com"
        assert data["role"] == "user"

    async def test_get_me_unauthorized(self, client: AsyncClient):
        response = await client.get(ME_URL)
        assert response.status_code == 401

    async def test_get_me_invalid_token(self, client: AsyncClient):
        response = await client.get(
            ME_URL,
            headers={"Authorization": "Bearer invalid_token_here"},
        )
        assert response.status_code == 401
