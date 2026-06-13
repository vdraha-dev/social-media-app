from collections.abc import AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx2 import ASGITransport, AsyncClient

from app.shared.domain.exceptions import (
    AlreadyExistsError,
    ConflictError,
    DomainError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from app.shared.events.event_bus import EventBus
from app.shared.presentation.exception_handlers import register_exception_handlers


@pytest.fixture
def domain_errors():
    return {
        "not_found": NotFoundError("User", 1),
        "already_exists": AlreadyExistsError("User", "email", "a@b.com"),
        "permission_denied": PermissionDeniedError("delete", "not admin"),
        "validation": ValidationError("invalid data"),
        "conflict": ConflictError("state conflict"),
        "generic": DomainError("something went wrong"),
    }


@pytest.fixture
def app() -> FastAPI:
    application = FastAPI()
    register_exception_handlers(application)
    return application


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def event_bus() -> EventBus:
    return EventBus()
