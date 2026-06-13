from unittest.mock import AsyncMock, MagicMock, patch
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
from app.identity.domain.value_objects import HashedPassword, Role, UserName
from app.shared.domain.value_objects import Email


@pytest.fixture
def mock_user_repo():
    return AsyncMock()


@pytest.fixture
def mock_token_repo():
    return AsyncMock()


@pytest.fixture
def mock_hasher():
    return MagicMock()


@pytest.fixture
def mock_token_service():
    return MagicMock()


@pytest.fixture
def sample_user():
    return User(
        username=UserName("testuser"),
        email=Email("test@example.com"),
        password=HashedPassword("hashed_pass"),
        role=Role(),
    )


class TestRegisterUserhandler:
    def setup_method(self):
        self.handler = RegisterUserhandler(
            user_repo=AsyncMock(),
            password_hasher=MagicMock(),
        )

    @pytest.mark.asyncio
    async def test_register_new_user(self, mock_user_repo, mock_hasher):
        mock_user_repo.exists_by_email = AsyncMock(return_value=False)
        mock_user_repo.save = AsyncMock()
        mock_hasher.hash.return_value = HashedPassword("hashed_val")

        handler = RegisterUserhandler(mock_user_repo, mock_hasher)
        request = RegisterUserRequest(
            username="newuser",
            email="new@example.com",
            password="plainpass",
        )

        await handler.handle(request)

        mock_user_repo.exists_by_email.assert_awaited_once_with("new@example.com")
        mock_user_repo.save.assert_awaited_once()
        mock_hasher.hash.assert_called_once_with("plainpass")

    @pytest.mark.asyncio
    async def test_raises_when_email_exists(self):
        mock_repo = AsyncMock()
        mock_repo.exists_by_email = AsyncMock(return_value=True)
        handler = RegisterUserhandler(
            mock_repo,
            MagicMock(),
        )
        request = RegisterUserRequest(
            username="user",
            email="exists@example.com",
            password="longenoughpass",
        )

        from app.identity.domain.exceptions import UserAlreadyExistsError

        with pytest.raises(UserAlreadyExistsError):
            await handler.handle(request)
        mock_repo.save.assert_not_called()


class TestLoginHandler:
    @pytest.mark.asyncio
    async def test_successful_login(self, sample_user):
        user_repo = AsyncMock()
        token_repo = AsyncMock()
        hasher = MagicMock()
        token_service = MagicMock()

        user_repo.get_by_email = AsyncMock(return_value=sample_user)
        hasher.verify.return_value = True
        token_service.generate.return_value = AccessToken(
            token="jwt_token",
            user_id=sample_user.id,
            expired_at=MagicMock(),
        )

        handler = LoginHandler(user_repo, token_repo, hasher, token_service)
        request = LoginRequest(email="test@example.com", password="plainpass")

        with patch(
            "app.identity.application.handlers.event_bus.publish",
            AsyncMock(),
        ) as mock_publish:
            result = await handler.handle(request)

        assert result.access_token == "jwt_token"
        assert result.token_type == "Bearer"
        user_repo.get_by_email.assert_awaited_once_with("test@example.com")
        hasher.verify.assert_called_once_with("plainpass", sample_user.password)
        user_repo.save.assert_awaited_once_with(sample_user)
        token_service.generate.assert_called_once_with(
            sample_user.id, sample_user.role.value
        )
        token_repo.save.assert_awaited_once()
        mock_publish.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_fails_when_user_not_found(self):
        user_repo = AsyncMock()
        user_repo.get_by_email = AsyncMock(return_value=None)

        handler = LoginHandler(
            user_repo,
            AsyncMock(),
            MagicMock(),
            MagicMock(),
        )
        request = LoginRequest(
            email="nouser@example.com",
            password="plainpass",
        )

        from app.identity.domain.exceptions import InvalidCredentialsError

        with pytest.raises(InvalidCredentialsError):
            await handler.handle(request)

    @pytest.mark.asyncio
    async def test_fails_when_password_wrong(self, sample_user):
        user_repo = AsyncMock()
        user_repo.get_by_email = AsyncMock(return_value=sample_user)
        hasher = MagicMock()
        hasher.verify.return_value = False

        handler = LoginHandler(
            user_repo,
            AsyncMock(),
            hasher,
            MagicMock(),
        )
        request = LoginRequest(
            email="test@example.com",
            password="wrongpass",
        )

        from app.identity.domain.exceptions import InvalidCredentialsError

        with pytest.raises(InvalidCredentialsError):
            await handler.handle(request)


class TestLogoutHandler:
    @pytest.mark.asyncio
    async def test_blacklists_tokens(self):
        token_repo = AsyncMock()
        handler = LogoutHandler(token_repo)
        user_id = uuid4()

        with patch(
            "app.identity.application.handlers.event_bus.publish",
            AsyncMock(),
        ) as mock_publish:
            await handler.handle(user_id)

        token_repo.blacklist_all_for_user.assert_awaited_once_with(user_id)
        mock_publish.assert_awaited_once()


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

        from app.identity.domain.exceptions import InvalidCredentialsError

        with pytest.raises(InvalidCredentialsError):
            await handler.handle("blacklisted_token")

    @pytest.mark.asyncio
    async def test_fails_when_token_not_found(self):
        user_repo = AsyncMock()
        token_repo = AsyncMock()
        token_service = MagicMock()

        token_service.decode.return_value = {"user_id": str(uuid4())}
        token_repo.get_by_token = AsyncMock(return_value=None)

        handler = VerifyUserByTokenHandler(user_repo, token_repo, token_service)

        from app.identity.domain.exceptions import InvalidCredentialsError

        with pytest.raises(InvalidCredentialsError):
            await handler.handle("nonexistent_token")

    @pytest.mark.asyncio
    async def test_fails_when_user_not_found(self):
        user_repo = AsyncMock()
        token_repo = AsyncMock()
        token_service = MagicMock()

        user_id = uuid4()
        token_service.decode.return_value = {"user_id": str(user_id)}
        token_repo.get_by_token = AsyncMock(
            return_value=AccessToken(
                token="token",
                user_id=user_id,
                expired_at=MagicMock(),
                blacklisted=False,
            )
        )
        user_repo.get_user_by_id = AsyncMock(return_value=None)

        handler = VerifyUserByTokenHandler(user_repo, token_repo, token_service)

        from app.identity.domain.exceptions import InvalidCredentialsError

        with pytest.raises(InvalidCredentialsError):
            await handler.handle("token")
