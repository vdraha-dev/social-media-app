import pytest
from httpx2 import AsyncClient


class TestAuthRegister:
    @pytest.mark.asyncio
    async def test_register_validation_error(self, client: AsyncClient):
        response = await client.post(
            "/auth/register",
            json={"username": "ab", "email": "bad", "password": "short"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_missing_fields(self, client: AsyncClient):
        response = await client.post("/auth/register", json={})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_invalid_json(self, client: AsyncClient):
        response = await client.post(
            "/auth/register",
            content="not-json",
            headers={"content-type": "application/json"},
        )
        assert response.status_code == 422


class TestAuthLogin:
    @pytest.mark.asyncio
    async def test_login_validation_error(self, client: AsyncClient):
        response = await client.post(
            "/auth/login",
            json={"email": "not-email", "password": ""},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_login_missing_fields(self, client: AsyncClient):
        response = await client.post("/auth/login", json={})
        assert response.status_code == 422


class TestAuthLogout:
    @pytest.mark.asyncio
    async def test_logout_without_token_returns_401(self, client: AsyncClient):
        response = await client.post("/auth/logout")
        assert response.status_code == 401


class TestAuthMe:
    @pytest.mark.asyncio
    async def test_get_me_without_token_returns_401(self, client: AsyncClient):
        response = await client.get("/auth/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_me_with_invalid_token_returns_401(self, client: AsyncClient):
        response = await client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token_format"},
        )
        assert response.status_code == 403
