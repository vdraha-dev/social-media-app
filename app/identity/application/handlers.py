from uuid import UUID

from app.identity.application.dto import (
    LoginRequest,
    RegisterUserRequest,
    TokenResponse,
    UserResponse,
)
from app.identity.domain.entities import User
from app.identity.domain.events import UserLogedIn, UserLoggedOut, UserRegistered
from app.identity.domain.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
)
from app.identity.domain.service import (
    IAccessTokenRepository,
    IPasswordHasher,
    ITokenService,
    IUserRepository,
)
from app.identity.domain.value_objects import Role, UserName
from app.shared.domain.value_objects import Email
from app.shared.events.event_bus import event_bus


class RegisterUserhandler:
    def __init__(self, user_repo: IUserRepository, password_hasher: IPasswordHasher):
        self.user_repo = user_repo
        self.hasher = password_hasher

    async def handle(self, request: RegisterUserRequest):
        if await self.user_repo.exists_by_email(request.email):
            raise UserAlreadyExistsError("User already exists with this email")

        user = User(
            username=UserName(request.username),
            email=Email(request.email),
            password=self.hasher.hash(request.password),
            role=Role(),
        )

        await self.user_repo.save(user)
        await event_bus.publish(
            UserRegistered(
                user_id=user.id, username=str(user.username), email=str(user.email)
            )
        )

        return UserResponse(
            id=user.id,
            username=str(user.username),
            email=str(user.email),
            role=str(user.role),
        )


class LoginHandler:
    def __init__(
        self,
        user_repo: IUserRepository,
        token_repo: IAccessTokenRepository,
        hasher: IPasswordHasher,
        token_service: ITokenService,
    ):
        self.user_repo = user_repo
        self.token_repo = token_repo
        self.hasher = hasher
        self.token_service = token_service

    async def handle(self, request: LoginRequest):
        user = await self.user_repo.get_by_email(request.email)

        if not user or not self.hasher.verify(request.password, user.password):
            raise InvalidCredentialsError(
                "Invalid credentials. Wrong email or password."
            )

        user.record_login()
        await self.user_repo.save(user)

        token = self.token_service.generate(user.id, user.role.value)
        await self.token_repo.save(token)

        await event_bus.publish(UserLogedIn(user_id=user.id))

        return TokenResponse(access_token=token.token, token_type="Bearer")


class LogoutHandler:
    def __init__(self, token_repo: IAccessTokenRepository):
        self.token_repo = token_repo

    async def handle(self, user_id: UUID):
        await self.token_repo.blacklist_all_for_user(user_id)
        await event_bus.publish(UserLoggedOut(user_id=user_id))


class VerifyUserByTokenHandler:
    def __init__(
        self,
        user_repo: IUserRepository,
        token_repo: IAccessTokenRepository,
        token_service: ITokenService,
    ):
        self.user_repo = user_repo
        self.token_repo = token_repo
        self.token_service = token_service

    async def handle(self, token_str: str) -> User:
        payload = self.token_service.decode(token_str)

        token = await self.token_repo.get_by_token(token_str)
        if not token or token.blacklisted:
            raise InvalidCredentialsError("Token is blacklisted")

        user = await self.user_repo.get_user_by_id(UUID(payload["user_id"]))

        if not user:
            raise InvalidCredentialsError("Invalid credentials")

        return user
