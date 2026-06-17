from uuid import UUID

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
from app.shared.domain.value_objects import Email
from app.shared.events.event_bus import event_bus


class RegisterUserUseCase:
    def __init__(self, user_repo: IUserRepository, password_hasher: IPasswordHasher):
        self.user_repo = user_repo
        self.hasher = password_hasher

    async def execute(self, new_user: User):
        if await self.user_repo.exists_by_email(new_user.email):
            raise UserAlreadyExistsError("User already exists with this email")

        await self.user_repo.save(new_user)
        await event_bus.publish(
            UserRegistered(
                user_id=new_user.id,
                username=str(new_user.username),
                email=str(new_user.email),
            )
        )


class LoginUseCase:
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

    async def handle(self, email: Email, password: str) -> str:
        user = await self.user_repo.get_by_email(email)

        if not user or not self.hasher.verify(password, user.password):
            raise InvalidCredentialsError(
                "Invalid credentials. Wrong email or password."
            )

        user.record_login()
        await self.user_repo.save(user)

        token = self.token_service.generate(user.id, user.role.value)
        await self.token_repo.save(token)

        await event_bus.publish(UserLogedIn(user_id=user.id))

        return token.token


class LogoutUseCase:
    def __init__(self, token_repo: IAccessTokenRepository):
        self.token_repo = token_repo

    async def handle(self, user_id: UUID):
        await self.token_repo.blacklist_all_for_user(user_id)
        await event_bus.publish(UserLoggedOut(user_id=user_id))


class AuthenticateUserByTokenUseCase:
    def __init__(
        self,
        user_repo: IUserRepository,
        token_repo: IAccessTokenRepository,
        token_service: ITokenService,
    ):
        self.user_repo = user_repo
        self.token_repo = token_repo
        self.token_service = token_service

    async def execute(self, token_str: str) -> User:
        payload = self.token_service.decode(token_str)

        token = await self.token_repo.get_by_token(token_str)
        if not token or token.blacklisted:
            raise InvalidCredentialsError("Token is blacklisted")

        user = await self.user_repo.get_user_by_id(UUID(payload["user_id"]))

        if not user:
            raise InvalidCredentialsError("Invalid credentials")

        return user


class GetUserIdByTokenUseCase:
    def __init__(self, token_service: ITokenService):
        self.token_service = token_service

    def sync_handle(self, token: str) -> UUID:
        return UUID(self.token_service.decode(token)["user_id"])
