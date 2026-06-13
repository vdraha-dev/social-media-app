from collections.abc import AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx2 import ASGITransport, AsyncClient

from app.identity.domain.entities import User
from app.identity.domain.value_objects import HashedPassword, Role, RoleEnum, UserName
from app.identity.infrastructure.security import PasswordHasher, TokenService
from app.identity.presentation.exception_handlers import register_exception_handlers
from app.identity.presentation.router import auth
from app.shared.domain.value_objects import Email


@pytest.fixture
def sample_user() -> User:
    return User(
        username=UserName("testuser"),
        email=Email("test@example.com"),
        password=HashedPassword("hashed_pass_placeholder"),
        role=Role(),
    )


@pytest.fixture
def admin_user() -> User:
    return User(
        username=UserName("admin"),
        email=Email("admin@example.com"),
        password=HashedPassword("hashed_pass_placeholder"),
        role=Role(RoleEnum.Admin),
    )


@pytest.fixture
def password_hasher() -> PasswordHasher:
    return PasswordHasher()


@pytest.fixture
def token_service() -> TokenService:
    return TokenService()


@pytest.fixture
def app() -> FastAPI:
    application = FastAPI()
    application.include_router(auth)
    register_exception_handlers(application)
    return application


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
