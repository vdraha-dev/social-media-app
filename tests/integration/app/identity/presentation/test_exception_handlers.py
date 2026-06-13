import pytest

from app.identity.domain.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
    UserAlreadyExistsError,
)


class TestExceptionHandlerRegistration:
    def test_all_identity_handlers_registered(self, app):
        handlers = app.exception_handlers
        for exc_type in [
            TokenExpiredError,
            InvalidTokenError,
            UserAlreadyExistsError,
            InvalidCredentialsError,
        ]:
            assert exc_type in handlers


class TestTokenExpiredHandler:
    @pytest.mark.asyncio
    async def test_returns_403(self, app):
        handler = app.exception_handlers[TokenExpiredError]
        response = await handler(None, TokenExpiredError("Token expired"))
        assert response.status_code == 403
        assert "Token expired" in response.body.decode()


class TestInvalidTokenHandler:
    @pytest.mark.asyncio
    async def test_returns_403(self, app):
        handler = app.exception_handlers[InvalidTokenError]
        response = await handler(None, InvalidTokenError("Invalid token"))
        assert response.status_code == 403


class TestUserAlreadyExistsHandler:
    @pytest.mark.asyncio
    async def test_returns_409(self, app):
        handler = app.exception_handlers[UserAlreadyExistsError]
        response = await handler(None, UserAlreadyExistsError("User exists"))
        assert response.status_code == 409


class TestInvalidCredentialsHandler:
    @pytest.mark.asyncio
    async def test_returns_401(self, app):
        handler = app.exception_handlers[InvalidCredentialsError]
        response = await handler(None, InvalidCredentialsError("Bad credentials"))
        assert response.status_code == 401
