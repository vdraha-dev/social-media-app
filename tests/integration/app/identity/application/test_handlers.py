from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.identity.application.dto import LoginRequest, RegisterUserRequest
from app.identity.application.handlers import (
    LoginHandler,
    LogoutHandler,
    RegisterUserhandler,
    VerifyUserByTokenHandler,
)
from app.identity.domain.entities import AccessToken, User
from app.identity.domain.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from app.identity.domain.value_objects import HashedPassword, Role, UserName
from app.shared.domain.value_objects import Email


class TestRegisterUserHandler:
    @pytest.mark.asyncio
    async def test_register_new_user(self):
        user_repo = AsyncMock()
        user_repo.exists_by_email = AsyncMock(return_value=False)
        user_repo.save = AsyncMock()
        hasher = MagicMock()
        hasher.hash.return_value = HashedPassword("hashed_val")

        handler = RegisterUserhandler(user_repo, hasher)
        request = RegisterUserRequest(
            username="newuser",
            email="new@example.com",
            password="plainpass",
        )

        result = await handler.handle(request)

        assert result.username == "newuser"
        assert result.email == "new@example.com"
        assert result.role == "user"
        user_repo.exists_by_email.assert_awaited_once_with("new@example.com")
        user_repo.save.assert_awaited_once()
        hasher.hash.assert_called_once_with("plainpass")

    @pytest.mark.asyncio
    async def test_raises_when_email_exists(self):
        user_repo = AsyncMock()
        user_repo.exists_by_email = AsyncMock(return_value=True)
        handler = RegisterUserhandler(user_repo, MagicMock())

        request = RegisterUserRequest(
            username="user",
            email="exists@example.com",
            password="longenoughpass",
        )

        with pytest.raises(UserAlreadyExistsError):
            await handler.handle(request)
        user_repo.save.assert_not_called()


class TestLoginHandler:
    @pytest.mark.asyncio
    async def test_successful_login(self):
        user = User(
            username=UserName("testuser"),
            email=Email("test@example.com"),
            password=HashedPassword("hashed_pass"),
            role=Role(),
        )
        user_repo = AsyncMock()
        user_repo.get_by_email = AsyncMock(return_value=user)
        user_repo.save = AsyncMock()

        token_repo = AsyncMock()
        hasher = MagicMock()
        hasher.verify.return_value = True

        token_service = MagicMock()
        token_service.generate.return_value = AccessToken(
            token="jwt_token",
            user_id=user.id,
            expired_at=MagicMock(),
        )

        handler = LoginHandler(user_repo, token_repo, hasher, token_service)
        request = LoginRequest(email="test@example.com", password="plainpass")

        result = await handler.handle(request)

        assert result.access_token == "jwt_token"
        assert result.token_type == "Bearer"
        user_repo.save.assert_awaited_once_with(user)
        token_repo.save.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_fails_when_user_not_found(self):
        user_repo = AsyncMock()
        user_repo.get_by_email = AsyncMock(return_value=None)

        handler = LoginHandler(user_repo, AsyncMock(), MagicMock(), MagicMock())
        request = LoginRequest(email="nouser@example.com", password="pass")

        with pytest.raises(InvalidCredentialsError):
            await handler.handle(request)

    @pytest.mark.asyncio
    async def test_fails_when_password_wrong(self):
        user = User(
            username=UserName("testuser"),
            email=Email("test@example.com"),
            password=HashedPassword("hashed_pass"),
            role=Role(),
        )
        user_repo = AsyncMock()
        user_repo.get_by_email = AsyncMock(return_value=user)

        hasher = MagicMock()
        hasher.verify.return_value = False

        handler = LoginHandler(user_repo, AsyncMock(), hasher, MagicMock())
        request = LoginRequest(email="test@example.com", password="wrongpass")

        with pytest.raises(InvalidCredentialsError):
            await handler.handle(request)


class TestLogoutHandler:
    @pytest.mark.asyncio
    async def test_blacklists_tokens_and_publishes_event(self):
        token_repo = AsyncMock()
        handler = LogoutHandler(token_repo)
        user_id = uuid4()

        await handler.handle(user_id)

        token_repo.blacklist_all_for_user.assert_awaited_once_with(user_id)


class TestVerifyUserByTokenHandler:
    @pytest.mark.asyncio
    async def test_verify_valid_token(self, sample_user):
        user_repo = AsyncMock()
        token_repo = AsyncMock()
        token_service = MagicMock()

        user_id = uuid4()
        token_service.decode.return_value = {"user_id": str(user_id)}
        token_repo.get_by_token = AsyncMock(
            return_value=AccessToken(
                token="valid_token",
                user_id=user_id,
                expired_at=MagicMock(),
                blacklisted=False,
            )
        )
        user_repo.get_user_by_id = AsyncMock(return_value=sample_user)

        handler = VerifyUserByTokenHandler(user_repo, token_repo, token_service)
        result = await handler.handle("valid_token")

        assert result is sample_user
        token_service.decode.assert_called_once_with("valid_token")
        token_repo.get_by_token.assert_awaited_once_with("valid_token")
        user_repo.get_user_by_id.assert_awaited_once_with(user_id)

    @pytest.mark.asyncio
    async def test_fails_when_token_blacklisted(self):
        user_repo = AsyncMock()
        token_repo = AsyncMock()
        token_service = MagicMock()

        token_service.decode.return_value = {"user_id": str(uuid4())}
        token_repo.get_by_token = AsyncMock(
            return_value=AccessToken(
                token="blacklisted_token",
                user_id=uuid4(),
                expired_at=MagicMock(),
                blacklisted=True,
            )
        )

        handler = VerifyUserByTokenHandler(user_repo, token_repo, token_service)
        with pytest.raises(InvalidCredentialsError):
            await handler.handle("blacklisted_token")

    @pytest.mark.asyncio
    async def test_fails_when_token_not_found(self):
        token_service = MagicMock()
        token_service.decode.return_value = {"user_id": str(uuid4())}

        handler = VerifyUserByTokenHandler(AsyncMock(), AsyncMock(), token_service)
        handler.token_repo.get_by_token = AsyncMock(return_value=None)

        with pytest.raises(InvalidCredentialsError):
            await handler.handle("nonexistent_token")
