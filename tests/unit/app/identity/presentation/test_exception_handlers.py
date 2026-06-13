from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI, Request

from app.identity.domain.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
    UserAlreadyExistsError,
)
from app.identity.presentation.exception_handlers import register_exception_handlers


@pytest.fixture
def app():
    return FastAPI()


@pytest.fixture
def mock_request():
    return MagicMock(spec=Request)


class TestRegisterExceptionHandlers:
    def test_registers_token_expired_handler(self, app):
        register_exception_handlers(app)
        assert TokenExpiredError in app.exception_handlers

    def test_registers_invalid_token_handler(self, app):
        register_exception_handlers(app)
        assert InvalidTokenError in app.exception_handlers

    def test_registers_user_already_exists_handler(self, app):
        register_exception_handlers(app)
        assert UserAlreadyExistsError in app.exception_handlers

    def test_registers_invalid_credentials_handler(self, app):
        register_exception_handlers(app)
        assert InvalidCredentialsError in app.exception_handlers


class TestTokenExpiredErrorHandler:
    @pytest.mark.asyncio
    async def test_returns_403(self, app, mock_request):
        register_exception_handlers(app)
        exc = TokenExpiredError("expired")
        handler = app.exception_handlers[TokenExpiredError]
        response = await handler(mock_request, exc)
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_contains_error_message(self, app, mock_request):
        register_exception_handlers(app)
        exc = TokenExpiredError("Token expired")
        handler = app.exception_handlers[TokenExpiredError]
        response = await handler(mock_request, exc)
        assert "expired" in response.body.decode()


class TestInvalidTokenErrorHandler:
    @pytest.mark.asyncio
    async def test_returns_403(self, app, mock_request):
        register_exception_handlers(app)
        exc = InvalidTokenError("bad token")
        handler = app.exception_handlers[InvalidTokenError]
        response = await handler(mock_request, exc)
        assert response.status_code == 403


class TestUserAlreadyExistsErrorHandler:
    @pytest.mark.asyncio
    async def test_returns_409(self, app, mock_request):
        register_exception_handlers(app)
        exc = UserAlreadyExistsError("user exists")
        handler = app.exception_handlers[UserAlreadyExistsError]
        response = await handler(mock_request, exc)
        assert response.status_code == 409


class TestInvalidCredentialsErrorHandler:
    @pytest.mark.asyncio
    async def test_returns_401(self, app, mock_request):
        register_exception_handlers(app)
        exc = InvalidCredentialsError("bad credentials")
        handler = app.exception_handlers[InvalidCredentialsError]
        response = await handler(mock_request, exc)
        assert response.status_code == 401
