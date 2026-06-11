from app.identity.application.dto import RegisterUserRequest, UserResponse
from app.identity.domain.entities import User
from app.identity.domain.errors import UserAlreadyExistsError
from app.identity.domain.events import UserRegistered
from app.identity.domain.service import IPasswordHasher, IUserRepository
from app.identity.domain.value_objects import Role
from app.shared.events import event_bus


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
