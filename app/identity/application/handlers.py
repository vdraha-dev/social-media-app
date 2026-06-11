from uuid import UUID

from app.identity.application.dto import (
    LoginRequest,
    RegisterUserRequest,
    TokenResponse,
    UserResponse,
)
from app.identity.domain.entities import User
from app.identity.domain.errors import InvalidCredentialsError, UserAlreadyExistsError
from app.identity.domain.events import UserLogedIn, UserLoggedOut, UserRegistered
from app.identity.domain.service import (
    IAccessTokenRepository,
    IPasswordHasher,
    ITokenService,
    IUserRepository,
)
from app.identity.domain.value_objects import Role
from app.shared.events.event_bus import event_bus


class RegisterUserhandler:
    def __init__(self, user_repo: IUserRepository, password_hasher: IPasswordHasher):
        self.user_repo = user_repo
        self.hasher = password_hasher

    async def handle(self, request: RegisterUserRequest):
        if await self.user_repo.exists_by_email(request.email):
            raise UserAlreadyExistsError("User already exists with this email")

        user = User(
            username=request.username,
            email=request.email,
            password=self.hasher.hash(request.password),
            role=Role(),
        )

        await self.user_repo.save(user)
        await event_bus.publish(
            UserRegistered(user_id=user.id, username=user.username, email=user.email)
        )

        return UserResponse(
            user_id=user.id, username=user.username, email=user.email, role=user.role
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

        if not user or self.hasher.verify(user.password, request.password):
            raise InvalidCredentialsError(
                "Invalid credentials. Wrong email or password."
            )

        user.record_login()
        await self.user_repo.save(user)

        token = self.token_service.generate(user.id, user.role)
        await self.token_repo.save(token)

        await event_bus.publish(UserLogedIn(user_id=user.id))

        return TokenResponse(access_token=token.access_token, token_type="Bearer")


class LogoutHandler:
    def __init__(self, token_repo: IAccessTokenRepository):
        self.token_repo = token_repo

    async def handle(self, user_id: UUID):
        await self.token_repo.blacklist_all_for_user(user_id)
        await event_bus.publish(UserLoggedOut(user_id=user_id))
