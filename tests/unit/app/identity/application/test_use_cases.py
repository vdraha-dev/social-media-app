from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest

from app.identity.application.dto import LoginRequest, RegisterUserRequest
from app.identity.application.use_cases import (
    AuthenticateUserByTokenUseCase,
    LoginUseCase,
    LogoutUseCase,
    RegisterUserUseCase,
)
from app.identity.domain.entities import User
from app.identity.domain.events import UserLoggedIn, UserLoggedOut, UserRegistered
from app.identity.domain.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from app.identity.domain.value_objects import HashedPassword, Role, UserName
from app.shared.domain.value_objects import Email
from app.shared.utils import uuid_gen


class TestRegisterUserUseCase:
    type UseCaseFixture = tuple[
        RegisterUserUseCase,
        MagicMock,
        MagicMock,
    ]

    @pytest.fixture
    def use_case(self) -> UseCaseFixture:
        user_repo = MagicMock()
        user_repo.exists_by_email = AsyncMock()
        user_repo.save = AsyncMock()
        password_hasher = MagicMock()
        return (
            RegisterUserUseCase(user_repo, password_hasher),
            user_repo,
            password_hasher,
        )

    async def test_register_user_success(self, use_case: UseCaseFixture):
        uc, user_repo, hasher = use_case
        user_repo.exists_by_email.return_value = False
        hasher.hash.return_value = HashedPassword(value="hashed")

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

        hasher.hash.assert_called_once_with("raw_password")
        user_repo.save.assert_awaited_once()
        saved_user = user_repo.save.call_args[0][0]
        assert isinstance(saved_user, User)
        assert saved_user.username == UserName("alice")
        assert saved_user.email == Email("alice@example.com")
        assert saved_user.password == HashedPassword(value="hashed")
        mock_publish.assert_awaited_once()
        args, _ = mock_publish.call_args
        published_event = args[0]
        assert isinstance(published_event, UserRegistered)
        assert published_event.user_id == saved_user.id

    async def test_register_user_already_exists(self, use_case: UseCaseFixture):
        uc, user_repo, _ = use_case
        user_repo.exists_by_email.return_value = True

        request = RegisterUserRequest(
            username="alice",
            email="alice@example.com",
            password="raw_password",
        )

        with pytest.raises(UserAlreadyExistsError, match="already exists"):
            await uc.execute(request)

        user_repo.exists_by_email.assert_awaited_once_with(Email("alice@example.com"))
        user_repo.save.assert_not_awaited()


class TestLoginUseCase:
    type LoginCaseFixture = tuple[
        LoginUseCase, MagicMock, MagicMock, MagicMock, MagicMock
    ]

    @pytest.fixture
    def use_case(self) -> LoginCaseFixture:
        user_repo = MagicMock()
        user_repo.get_by_email = AsyncMock()
        user_repo.save = AsyncMock()
        token_repo = MagicMock()
        token_repo.save = AsyncMock()
        hasher = MagicMock()
        token_service = MagicMock()
        return (
            LoginUseCase(user_repo, token_repo, hasher, token_service),
            user_repo,
            token_repo,
            hasher,
            token_service,
        )

    async def test_login_success(self, use_case: LoginCaseFixture):
        uc, user_repo, token_repo, hasher, token_service = use_case
        request = LoginRequest(email="alice@example.com", password="correct_password")
        user = User(
            username=UserName(value="alice"),
            email=Email(value="alice@example.com"),
            password=HashedPassword(value="hashed"),
            role=Role(),
            id=uuid_gen(),
        )
        user_repo.get_by_email.return_value = user
        hasher.verify.return_value = True
        token_service.generate.return_value = MagicMock(token="jwt_token")

        with patch(
            "app.identity.application.use_cases.event_bus.publish",
            new_callable=AsyncMock,
        ) as mock_publish:
            result = await uc.execute(request)

        assert result.access_token == "jwt_token"
        user_repo.get_by_email.assert_awaited_once_with(Email("alice@example.com"))
        hasher.verify.assert_called_once_with("correct_password", user.password)
        user_repo.save.assert_awaited_once_with(user)
        token_service.generate.assert_called_once_with(user.id, user.role.value)
        token_repo.save.assert_awaited_once()
        mock_publish.assert_awaited_once()
        args, _ = mock_publish.call_args
        assert isinstance(args[0], UserLoggedIn)
        assert args[0].user_id == user.id

    async def test_login_invalid_email(self, use_case: LoginCaseFixture):
        uc, user_repo, _, hasher, _ = use_case
        user_repo.get_by_email.return_value = None

        with pytest.raises(InvalidCredentialsError, match="Invalid credentials"):
            await uc.execute(
                LoginRequest(email="unknown@example.com", password="password")
            )

        hasher.verify.assert_not_called()

    async def test_login_invalid_password(self, use_case: LoginCaseFixture):
        uc, user_repo, _, hasher, _ = use_case
        user = User(
            username=UserName(value="alice"),
            email=Email(value="alice@example.com"),
            password=HashedPassword(value="hashed"),
            role=Role(),
        )
        user_repo.get_by_email.return_value = user
        hasher.verify.return_value = False

        with pytest.raises(InvalidCredentialsError, match="Invalid credentials"):
            await uc.execute(
                LoginRequest(email="alice@example.com", password="wrong_password")
            )

        hasher.verify.assert_called_once_with("wrong_password", user.password)


class TestLogoutUseCase:
    type LogoutCaseFixture = tuple[LogoutUseCase, MagicMock]

    @pytest.fixture
    def use_case(self) -> LogoutCaseFixture:
        token_repo = MagicMock()
        token_repo.blacklist_all_for_user = AsyncMock()
        return LogoutUseCase(token_repo), token_repo

    async def test_logout_success(self, use_case: LogoutCaseFixture):
        uc, token_repo = use_case
        user_id = uuid_gen()

        with patch(
            "app.identity.application.use_cases.event_bus.publish",
            new_callable=AsyncMock,
        ) as mock_publish:
            await uc.execute(user_id)

        token_repo.blacklist_all_for_user.assert_awaited_once_with(user_id)
        mock_publish.assert_awaited_once()
        args, _ = mock_publish.call_args
        assert isinstance(args[0], UserLoggedOut)
        assert args[0].user_id == user_id


class TestAuthenticateUserByTokenUseCase:
    type AuthCaseFixture = tuple[AuthenticateUserByTokenUseCase, MagicMock, MagicMock]

    @pytest.fixture
    def use_case(self) -> AuthCaseFixture:
        token_repo = MagicMock()
        token_repo.get_by_token = AsyncMock()
        token_service = MagicMock()
        return (
            AuthenticateUserByTokenUseCase(token_repo, token_service),
            token_repo,
            token_service,
        )

    async def test_authenticate_success(self, use_case: AuthCaseFixture):
        uc, token_repo, token_service = use_case
        user_id = uuid_gen()
        token_service.decode.return_value = {"user_id": str(user_id)}
        token_repo.get_by_token.return_value = MagicMock(
            token="valid_token",
            blacklisted=False,
        )

        result = await uc.execute("valid_token")

        assert result == user_id
        assert isinstance(result, UUID)
        token_service.decode.assert_called_once_with("valid_token")
        token_repo.get_by_token.assert_awaited_once_with("valid_token")

    async def test_authenticate_blacklisted_token(self, use_case: AuthCaseFixture):
        uc, token_repo, token_service = use_case
        token_service.decode.return_value = {"user_id": str(uuid_gen())}
        token_repo.get_by_token.return_value = MagicMock(
            token="blacklisted_token",
            blacklisted=True,
        )

        with pytest.raises(InvalidCredentialsError, match="blacklisted"):
            await uc.execute("blacklisted_token")

    async def test_authenticate_token_not_found(self, use_case: AuthCaseFixture):
        uc, token_repo, token_service = use_case
        token_service.decode.return_value = {"user_id": str(uuid_gen())}
        token_repo.get_by_token.return_value = None

        with pytest.raises(InvalidCredentialsError, match="blacklisted"):
            await uc.execute("unknown_token")
