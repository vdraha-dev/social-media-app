from datetime import datetime
from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest
from pytz import UTC
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.identity.application.dto import LoginRequest, RegisterUserRequest
from app.identity.application.use_cases import (
    AuthenticateUserByTokenUseCase,
    LoginUseCase,
    LogoutUseCase,
    RegisterUserUseCase,
)
from app.identity.domain.events import UserLoggedIn, UserLoggedOut, UserRegistered
from app.identity.domain.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from app.identity.domain.value_objects import HashedPassword, Role, UserName
from app.identity.infrastructure.models import AccessTokenModel, UserModel
from app.identity.infrastructure.repository import AccessTokenRepository, UserRepository
from app.identity.infrastructure.security import PasswordHasher, TokenService
from app.shared.domain.value_objects import Email


class TestRegisterUserUseCase:
    async def test_register_user_success(self, session: AsyncSession):
        user_repo = UserRepository(session)
        hasher = PasswordHasher()
        uc = RegisterUserUseCase(user_repo, hasher)

        request = RegisterUserRequest(
            username="alice",
            email="alice@example.com",
            password="raw_password",
        )

        with patch(
            "app.identity.application.use_cases.event_bus.publish",
            new_callable=AsyncMock,
        ) as mock_publish:
            await uc.execute(request)

        stmt = select(UserModel).where(UserModel.email == Email("alice@example.com"))
        result = await session.execute(stmt)
        loaded = result.scalar_one()
        assert loaded.username == UserName("alice")
        assert loaded.email == Email("alice@example.com")
        assert loaded.password_hash != HashedPassword("raw")
        assert loaded.role == Role()

        mock_publish.assert_awaited_once()
        args, _ = mock_publish.call_args
        assert isinstance(args[0], UserRegistered)
        assert args[0].user_id == loaded.id

    async def test_register_user_already_exists(self, session: AsyncSession):
        user_m = UserModel(
            username=UserName("existing"),
            email=Email("existing@example.com"),
            password_hash=HashedPassword("hash"),
        )
        session.add(user_m)
        await session.flush()

        user_repo = UserRepository(session)
        hasher = PasswordHasher()
        uc = RegisterUserUseCase(user_repo, hasher)

        request = RegisterUserRequest(
            username="duplicate",
            email="existing@example.com",
            password="raw_password",
        )

        with pytest.raises(UserAlreadyExistsError, match="already exists"):
            await uc.execute(request)


class TestLoginUseCase:
    async def test_login_success(self, session: AsyncSession):
        hasher = PasswordHasher()
        hashed = hasher.hash("correct_password")

        user_m = UserModel(
            username=UserName("alice"),
            email=Email("alice@example.com"),
            password_hash=hashed,
        )
        session.add(user_m)
        await session.flush()

        user_repo = UserRepository(session)
        token_repo = AccessTokenRepository(session)
        token_service = TokenService()
        uc = LoginUseCase(user_repo, token_repo, hasher, token_service)

        request = LoginRequest(email="alice@example.com", password="correct_password")

        with patch(
            "app.identity.application.use_cases.event_bus.publish",
            new_callable=AsyncMock,
        ) as mock_publish:
            token_response = await uc.execute(request)

        assert isinstance(token_response.access_token, str)
        assert len(token_response.access_token) > 0

        stmt = select(AccessTokenModel).where(
            AccessTokenModel.token == token_response.access_token
        )
        result = await session.execute(stmt)
        token_loaded = result.scalar_one()
        assert token_loaded.user_id == user_m.id
        assert token_loaded.blacklisted is False

        stmt = select(UserModel).where(UserModel.id == user_m.id)
        result = await session.execute(stmt)
        user_loaded = result.scalar_one()
        assert user_loaded.last_login is not None
        assert user_loaded.last_login.tzinfo is not None

        mock_publish.assert_awaited_once()
        args, _ = mock_publish.call_args
        assert isinstance(args[0], UserLoggedIn)
        assert args[0].user_id == user_m.id

    async def test_login_invalid_email(self, session: AsyncSession):
        user_repo = UserRepository(session)
        token_repo = AccessTokenRepository(session)
        hasher = PasswordHasher()
        token_service = TokenService()
        uc = LoginUseCase(user_repo, token_repo, hasher, token_service)

        with pytest.raises(InvalidCredentialsError, match="Invalid credentials"):
            await uc.execute(
                LoginRequest(email="unknown@example.com", password="password")
            )

    async def test_login_invalid_password(self, session: AsyncSession):
        hasher = PasswordHasher()
        hashed = hasher.hash("correct_password")

        user_m = UserModel(
            username=UserName("alice"),
            email=Email("alice@example.com"),
            password_hash=hashed,
        )
        session.add(user_m)
        await session.flush()

        user_repo = UserRepository(session)
        token_repo = AccessTokenRepository(session)
        token_service = TokenService()
        uc = LoginUseCase(user_repo, token_repo, hasher, token_service)

        with pytest.raises(InvalidCredentialsError, match="Invalid credentials"):
            await uc.execute(
                LoginRequest(email="alice@example.com", password="wrong_password")
            )


class TestLogoutUseCase:
    async def test_logout_success(self, session: AsyncSession):
        user_m = UserModel(
            username=UserName("logout-user"),
            email=Email("logout-user@example.com"),
            password_hash=HashedPassword("hash"),
        )
        session.add(user_m)
        await session.flush()

        now = datetime.now(UTC)
        token_a = AccessTokenModel(
            token="logout-token-a",
            user_id=user_m.id,
            expired_at=now,
            blacklisted=False,
        )
        token_b = AccessTokenModel(
            token="logout-token-b",
            user_id=user_m.id,
            expired_at=datetime.now(UTC),
            blacklisted=False,
        )
        session.add_all([token_a, token_b])
        await session.flush()

        token_repo = AccessTokenRepository(session)
        uc = LogoutUseCase(token_repo)

        with patch(
            "app.identity.application.use_cases.event_bus.publish",
            new_callable=AsyncMock,
        ) as mock_publish:
            await uc.execute(user_m.id)

        stmt = select(AccessTokenModel).where(AccessTokenModel.user_id == user_m.id)
        result = await session.execute(stmt)
        tokens = result.scalars().all()
        assert all(t.blacklisted for t in tokens)

        mock_publish.assert_awaited_once()
        args, _ = mock_publish.call_args
        assert isinstance(args[0], UserLoggedOut)
        assert args[0].user_id == user_m.id


class TestAuthenticateUserByTokenUseCase:
    async def test_authenticate_success(self, session: AsyncSession):
        hasher = PasswordHasher()
        user_m = UserModel(
            username=UserName("auth-user"),
            email=Email("auth-user@example.com"),
            password_hash=hasher.hash("password"),
        )
        session.add(user_m)
        await session.flush()

        token_service = TokenService()
        access_token = token_service.generate(user_m.id, "user")

        token_m = AccessTokenModel(
            token=access_token.token,
            user_id=user_m.id,
            expired_at=access_token.expired_at,
            blacklisted=False,
        )
        session.add(token_m)
        await session.flush()

        token_repo = AccessTokenRepository(session)
        uc = AuthenticateUserByTokenUseCase(token_repo, token_service)

        result = await uc.execute(access_token.token)

        assert isinstance(result, UUID)
        assert result == user_m.id

    async def test_authenticate_blacklisted_token(self, session: AsyncSession):
        user_m = UserModel(
            username=UserName("blacklisted-user"),
            email=Email("blacklisted-user@example.com"),
            password_hash=HashedPassword("hash"),
        )
        session.add(user_m)
        await session.flush()

        token_service = TokenService()
        access_token = token_service.generate(user_m.id, "user")

        token_m = AccessTokenModel(
            token=access_token.token,
            user_id=user_m.id,
            expired_at=access_token.expired_at,
            blacklisted=True,
        )
        session.add(token_m)
        await session.flush()

        token_repo = AccessTokenRepository(session)
        uc = AuthenticateUserByTokenUseCase(token_repo, token_service)

        with pytest.raises(InvalidCredentialsError, match="blacklisted"):
            await uc.execute(access_token.token)

    async def test_authenticate_token_not_found(self, session: AsyncSession):
        token_service = TokenService()
        user_id = UUID("00000000-0000-0000-0000-000000000000")
        access_token = token_service.generate(user_id, "user")

        token_repo = AccessTokenRepository(session)
        uc = AuthenticateUserByTokenUseCase(token_repo, token_service)

        with pytest.raises(InvalidCredentialsError, match="blacklisted"):
            await uc.execute(access_token.token)
