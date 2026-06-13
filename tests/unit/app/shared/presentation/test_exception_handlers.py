from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI, Request

from app.shared.domain.exceptions import (
    AlreadyExistsError,
    ConflictError,
    DomainError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from app.shared.presentation.exception_handlers import register_exception_handlers


@pytest.fixture
def app():
    return FastAPI()


@pytest.fixture
def mock_request():
    request = MagicMock(spec=Request)
    return request


class TestRegisterExceptionHandlers:
    def test_registers_not_found_handler(self, app):
        register_exception_handlers(app)
        handlers = app.exception_handlers
        assert NotFoundError in handlers

    def test_registers_already_exists_handler(self, app):
        register_exception_handlers(app)
        handlers = app.exception_handlers
        assert AlreadyExistsError in handlers

    def test_registers_permission_denied_handler(self, app):
        register_exception_handlers(app)
        handlers = app.exception_handlers
        assert PermissionDeniedError in handlers

    def test_registers_validation_handler(self, app):
        register_exception_handlers(app)
        handlers = app.exception_handlers
        assert ValidationError in handlers

    def test_registers_conflict_handler(self, app):
        register_exception_handlers(app)
        handlers = app.exception_handlers
        assert ConflictError in handlers

    def test_registers_domain_error_handler(self, app):
        register_exception_handlers(app)
        handlers = app.exception_handlers
        assert DomainError in handlers


class TestPermissionDeniedErrorHandler:
    @pytest.mark.asyncio
    async def test_returns_403(self, app, mock_request):
        register_exception_handlers(app)
        exc = PermissionDeniedError("delete")
        handler = app.exception_handlers[PermissionDeniedError]
        response = await handler(mock_request, exc)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_contains_detail_and_code(self, app, mock_request):
        register_exception_handlers(app)
        exc = PermissionDeniedError("delete", "not admin")
        handler = app.exception_handlers[PermissionDeniedError]
        response = await handler(mock_request, exc)
        body = response.body.decode()
        assert "PERMISSION_DENIED" in body


class TestValidationErrorHandler:
    @pytest.mark.asyncio
    async def test_returns_422(self, app, mock_request):
        register_exception_handlers(app)
        exc = ValidationError("bad data")
        handler = app.exception_handlers[ValidationError]
        response = await handler(mock_request, exc)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_contains_detail_and_code(self, app, mock_request):
        register_exception_handlers(app)
        exc = ValidationError("bad data")
        handler = app.exception_handlers[ValidationError]
        response = await handler(mock_request, exc)
        body = response.body.decode()
        assert "VALIDATION_ERROR" in body


class TestConflictErrorHandler:
    @pytest.mark.asyncio
    async def test_returns_409(self, app, mock_request):
        register_exception_handlers(app)
        exc = ConflictError("state conflict")
        handler = app.exception_handlers[ConflictError]
        response = await handler(mock_request, exc)
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_contains_detail_and_code(self, app, mock_request):
        register_exception_handlers(app)
        exc = ConflictError("state conflict")
        handler = app.exception_handlers[ConflictError]
        response = await handler(mock_request, exc)
        body = response.body.decode()
        assert "CONFLICT" in body


class TestDomainErrorHandler:
    @pytest.mark.asyncio
    async def test_returns_400(self, app, mock_request):
        register_exception_handlers(app)
        exc = DomainError("generic error")
        handler = app.exception_handlers[DomainError]
        response = await handler(mock_request, exc)
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_contains_detail_and_code(self, app, mock_request):
        register_exception_handlers(app)
        exc = DomainError("generic error")
        handler = app.exception_handlers[DomainError]
        response = await handler(mock_request, exc)
        body = response.body.decode()
        assert "DOMAIN_ERROR" in body
