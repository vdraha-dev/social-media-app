import pytest
from httpx2 import AsyncClient

from app.shared.domain.exceptions import (
    AlreadyExistsError,
    ConflictError,
    DomainError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)


class TestExceptionHandlerRegistration:
    def test_all_handlers_registered(self, app):
        handlers = app.exception_handlers
        for exc_type in [
            NotFoundError,
            AlreadyExistsError,
            PermissionDeniedError,
            ValidationError,
            ConflictError,
            DomainError,
        ]:
            assert exc_type in handlers, f"{exc_type.__name__} not registered"


class TestNotFoundErrorHandler:
    @pytest.mark.asyncio
    async def test_returns_404_json(self, app, client: AsyncClient):
        exc = NotFoundError("User", 42)
        handler = client._transport.app.exception_handlers[NotFoundError]
        response = await handler(None, exc)
        assert response.status_code == 404
        body = response.body.decode()
        assert "NOT_FOUND" in body
        assert "User" in body

    @pytest.mark.asyncio
    async def test_404_response_structure(self, app, client: AsyncClient):
        handler = app.exception_handlers[NotFoundError]
        response = await handler(None, NotFoundError("Post", "abc"))
        body = response.body.decode()
        assert "detail" in body or '"detail"' in body
        assert "NOT_FOUND" in body


class TestAlreadyExistsErrorHandler:
    @pytest.mark.asyncio
    async def test_returns_409_json(self, app, client: AsyncClient):
        exc = AlreadyExistsError("User", "email", "a@b.com")
        handler = app.exception_handlers[AlreadyExistsError]
        response = await handler(None, exc)
        assert response.status_code == 409
        body = response.body.decode()
        assert "ALREADY_EXISTS" in body

    @pytest.mark.asyncio
    async def test_409_response_structure(self, app, client: AsyncClient):
        handler = app.exception_handlers[AlreadyExistsError]
        response = await handler(None, AlreadyExistsError("Product", "sku", "X1"))
        assert response.status_code == 409


class TestPermissionDeniedErrorHandler:
    @pytest.mark.asyncio
    async def test_returns_403_json(self, app, client: AsyncClient):
        exc = PermissionDeniedError("delete", "not admin")
        handler = app.exception_handlers[PermissionDeniedError]
        response = await handler(None, exc)
        assert response.status_code == 403
        body = response.body.decode()
        assert "PERMISSION_DENIED" in body

    @pytest.mark.asyncio
    async def test_403_without_reason(self, app, client: AsyncClient):
        handler = app.exception_handlers[PermissionDeniedError]
        response = await handler(None, PermissionDeniedError("write"))
        assert response.status_code == 403


class TestValidationErrorHandler:
    @pytest.mark.asyncio
    async def test_returns_422_json(self, app, client: AsyncClient):
        exc = ValidationError("invalid input")
        handler = app.exception_handlers[ValidationError]
        response = await handler(None, exc)
        assert response.status_code == 422
        body = response.body.decode()
        assert "VALIDATION_ERROR" in body

    @pytest.mark.asyncio
    async def test_422_without_message(self, app, client: AsyncClient):
        handler = app.exception_handlers[ValidationError]
        response = await handler(None, ValidationError())
        assert response.status_code == 422


class TestConflictErrorHandler:
    @pytest.mark.asyncio
    async def test_returns_409_json(self, app, client: AsyncClient):
        exc = ConflictError("duplicate entry")
        handler = app.exception_handlers[ConflictError]
        response = await handler(None, exc)
        assert response.status_code == 409
        body = response.body.decode()
        assert "CONFLICT" in body

    @pytest.mark.asyncio
    async def test_conflict_without_message(self, app, client: AsyncClient):
        handler = app.exception_handlers[ConflictError]
        response = await handler(None, ConflictError())
        assert response.status_code == 409


class TestGenericDomainErrorHandler:
    @pytest.mark.asyncio
    async def test_returns_400_json(self, app, client: AsyncClient):
        exc = DomainError("something broke")
        handler = app.exception_handlers[DomainError]
        response = await handler(None, exc)
        assert response.status_code == 400
        body = response.body.decode()
        assert "DOMAIN_ERROR" in body

    @pytest.mark.asyncio
    async def test_generic_catch_all(self, app, client: AsyncClient):
        handler = app.exception_handlers[DomainError]
        response = await handler(None, DomainError("unknown"))
        assert response.status_code == 400
