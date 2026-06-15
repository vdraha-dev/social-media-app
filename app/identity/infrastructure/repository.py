from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.identity.domain.entities import AccessToken, User
from app.identity.domain.service import IAccessTokenRepository, IUserRepository
from app.identity.domain.value_objects import HashedPassword, Role, UserName
from app.identity.infrastructure.models import AccessTokenModel, UserModel
from app.shared.domain.value_objects import Email


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        user = await self.session.get(UserModel, user_id)
        return self._to_entity(user) if user else None

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        return self._to_entity(user) if user else None

    async def save(self, user: User):
        user_m = await self.session.get(UserModel, user.id)
        if user_m:
            user_m.username = str(user.username)
            user_m.email = str(user.email)
            user_m.password_hash = str(user.password)
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
        e = User(
            # id=m.id,
            username=UserName(m.username),
            email=Email(m.email),
            password=HashedPassword(m.password_hash),
            role=Role(m.role),
            last_login=m.last_login,
            # created_at=m.created_at,
            # updated_at=m.updated_at,
        )

        e.id = m.id
        e.created_at = m.created_at
        e.updated_at = m.updated_at

        return e

    def _to_model(self, e: User) -> UserModel:
        return UserModel(
            id=e.id,
            username=str(e.username),
            email=str(e.email),
            password_hash=str(e.password),
            role=str(e.role),
            last_login=e.last_login,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )


class AccessTokenRepository(IAccessTokenRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_token(self, token: str) -> AccessToken | None:
        stmt = select(AccessTokenModel).where(AccessTokenModel.token == token)
        result = await self.session.execute(stmt)
        access_token = result.scalar_one_or_none()
        return self._to_entity(access_token) if access_token else None

    async def save(self, access_token: AccessToken):
        self.session.add(self._to_model(access_token))
        await self.session.flush()

    async def blacklist_all_for_user(self, user_id: UUID):
        stmt = (
            update(AccessTokenModel)
            .where(AccessTokenModel.user_id == user_id)
            .values(blacklisted=True)
        )

        await self.session.execute(stmt)

    def _to_model(self, e: AccessToken) -> AccessTokenModel:
        return AccessTokenModel(
            id=e.id,
            created_at=e.created_at,
            updated_at=e.updated_at,
            token=e.token,
            user_id=e.user_id,
            expired_at=e.expired_at,
            blacklisted=e.blacklisted,
        )

    def _to_entity(self, m: AccessTokenModel) -> AccessToken:
        token = AccessToken(
            # id=m.id,
            # created_at=m.created_at,
            # updated_at=m.updated_at,
            token=m.token,
            user_id=m.user_id,
            expired_at=m.expired_at,
            blacklisted=m.blacklisted,
        )
        token.id = m.id
        token.created_at = m.created_at
        token.updated_at = m.updated_at

        return token
