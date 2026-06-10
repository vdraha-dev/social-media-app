import select
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.identity.domain.entities import User
from app.identity.domain.service import IUserRepository
from app.identity.domain.value_objects import HashedPassword, Role
from app.identity.infrastructure.models import UserModel
from app.shared.domain.value_objects import Email


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        user = self.session.get(UserModel, user_id)
        return self._to_entity(user) if user else None

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        return self._to_entity(user) if user else None

    async def save(self, user: User):
        user_m = self.session.get(UserModel, user.id)
        if user_m:
            user_m.username = user.username
            user_m.email = user.email
            user_m.password_hash = user.password
            user_m.role = user.role.value
            user_m.last_login = user.last_login
            user_m.updated_at = user.updated_at
        else:
            self.session.add(self._to_model(user))
        await self.session.flush()

    async def exists_by_email(self, email: str) -> bool:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        return user is not None

    def _to_entity(self, m: UserModel) -> User:
        return User(
            id=m.id,
            username=m.username,
            email=Email(m.email),
            password=HashedPassword(m.password),
            role=Role(m.role),
            last_login=m.last_login,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    def _to_model(self, e: User) -> UserModel:
        return UserModel(
            id=e.id,
            username=e.username,
            email=str(e.email),
            password=e.password.value,
            role=e.role.value,
            last_login=e.last_login,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )
