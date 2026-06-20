from datetime import datetime
from uuid import UUID

from pytz import UTC
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.identity.domain.entities import AccessToken, User
from app.identity.domain.value_objects import HashedPassword, Role, RoleEnum, UserName
from app.identity.infrastructure.models import AccessTokenModel, UserModel
from app.identity.infrastructure.repository import AccessTokenRepository, UserRepository
from app.shared.domain.value_objects import Email


class TestUserRepositoryGetUserById:
    async def test_returns_user_when_found(self, session: AsyncSession):
        user_m = UserModel(
            username="alice",
            email="alice@example.com",
            password_hash="hashed_pw",
        )
        session.add(user_m)
        await session.flush()

        repo = UserRepository(session)
        result = await repo.get_user_by_id(user_m.id)

        assert isinstance(result, User)
        assert result.id == user_m.id
        assert result.username == UserName(value="alice")
        assert result.email == Email(value="alice@example.com")

    async def test_returns_none_when_not_found(self, session: AsyncSession):
        repo = UserRepository(session)
        result = await repo.get_user_by_id(UUID("00000000-0000-0000-0000-000000000000"))
        assert result is None


class TestUserRepositoryGetByEmail:
    async def test_returns_user_when_found(self, session: AsyncSession):
        user_m = UserModel(
            username="bob",
            email="bob@example.com",
            password_hash="hashed_pw",
        )
        session.add(user_m)
        await session.flush()

        repo = UserRepository(session)
        result = await repo.get_by_email(Email(value="bob@example.com"))

        assert isinstance(result, User)
        assert result.username == UserName(value="bob")
        assert result.email == Email(value="bob@example.com")

    async def test_returns_none_when_not_found(self, session: AsyncSession):
        repo = UserRepository(session)
        result = await repo.get_by_email(Email(value="nobody@example.com"))
        assert result is None


class TestUserRepositorySave:
    async def test_inserts_new_user(self, session: AsyncSession):
        repo = UserRepository(session)
        user = User(
            username=UserName(value="charlie"),
            email=Email(value="charlie@example.com"),
            password=HashedPassword(value="hash"),
            role=Role(),
        )

        await repo.save(user)

        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await session.execute(stmt)
        loaded = result.scalar_one()
        assert loaded.username == "charlie"
        assert loaded.email == "charlie@example.com"
        assert loaded.password_hash == "hash"

    async def test_updates_existing_user(self, session: AsyncSession):
        user_m = UserModel(
            username="old",
            email="old@example.com",
            password_hash="old_hash",
        )
        session.add(user_m)
        await session.flush()

        repo = UserRepository(session)
        user = User(
            username=UserName(value="new"),
            email=Email(value="new@example.com"),
            password=HashedPassword(value="new_hash"),
            role=Role(),
            id=user_m.id,
            created_at=user_m.created_at,
            updated_at=user_m.updated_at,
        )

        await repo.save(user)

        stmt = select(UserModel).where(UserModel.id == user_m.id)
        result = await session.execute(stmt)
        loaded = result.scalar_one()
        assert loaded.username == "new"
        assert loaded.email == "new@example.com"
        assert loaded.password_hash == "new_hash"

    async def test_updates_role_and_last_login(self, session: AsyncSession):
        user_m = UserModel(
            username="role-update",
            email="role-update@example.com",
            password_hash="hash",
            role=RoleEnum.User,
        )
        session.add(user_m)
        await session.flush()

        now = datetime.now(UTC)
        repo = UserRepository(session)
        user = User(
            username=UserName(value="role-update"),
            email=Email(value="role-update@example.com"),
            password=HashedPassword(value="hash"),
            role=Role(RoleEnum.Admin),
            last_login=now,
            id=user_m.id,
            created_at=user_m.created_at,
            updated_at=user_m.updated_at,
        )

        await repo.save(user)

        stmt = select(UserModel).where(UserModel.id == user_m.id)
        result = await session.execute(stmt)
        loaded = result.scalar_one()
        assert loaded.role == RoleEnum.Admin
        assert loaded.last_login == now


class TestUserRepositoryExistsByEmail:
    async def test_returns_true_when_exists(self, session: AsyncSession):
        user_m = UserModel(
            username="exists-user",
            email="exists@example.com",
            password_hash="hash",
        )
        session.add(user_m)
        await session.flush()

        repo = UserRepository(session)
        result = await repo.exists_by_email(Email(value="exists@example.com"))
        assert result is True

    async def test_returns_false_when_not_exists(self, session: AsyncSession):
        repo = UserRepository(session)
        result = await repo.exists_by_email(Email(value="missing@example.com"))
        assert result is False


class TestAccessTokenRepositoryGetByToken:
    async def test_returns_token_when_found(self, session: AsyncSession):
        user_m = UserModel(
            username="token-owner",
            email="token-owner@example.com",
            password_hash="hash",
        )
        session.add(user_m)
        await session.flush()

        token_m = AccessTokenModel(
            token="test-token-123",
            user_id=user_m.id,
            expired_at=datetime.now(UTC),
            blacklisted=False,
        )
        session.add(token_m)
        await session.flush()

        repo = AccessTokenRepository(session)
        result = await repo.get_by_token("test-token-123")

        assert isinstance(result, AccessToken)
        assert result.token == "test-token-123"
        assert result.user_id == user_m.id
        assert result.blacklisted is False

    async def test_returns_none_when_not_found(self, session: AsyncSession):
        repo = AccessTokenRepository(session)
        result = await repo.get_by_token("unknown-token")
        assert result is None


class TestAccessTokenRepositorySave:
    async def test_adds_token_to_database(self, session: AsyncSession):
        user_m = UserModel(
            username="token-save-user",
            email="token-save-user@example.com",
            password_hash="hash",
        )
        session.add(user_m)
        await session.flush()

        repo = AccessTokenRepository(session)
        token = AccessToken(
            token="saved-token",
            user_id=user_m.id,
            expired_at=datetime.now(UTC),
        )

        await repo.save(token)

        stmt = select(AccessTokenModel).where(AccessTokenModel.id == token.id)
        result = await session.execute(stmt)
        loaded = result.scalar_one()
        assert loaded.token == "saved-token"
        assert loaded.user_id == user_m.id
        assert loaded.blacklisted is False


class TestAccessTokenRepositoryBlacklistAllForUser:
    async def test_blacklists_all_tokens_for_user(self, session: AsyncSession):
        user_m = UserModel(
            username="blacklist-user",
            email="blacklist-user@example.com",
            password_hash="hash",
        )
        session.add(user_m)
        await session.flush()

        token_a = AccessTokenModel(
            token="blacklist-token-a",
            user_id=user_m.id,
            expired_at=datetime.now(UTC),
            blacklisted=False,
        )
        token_b = AccessTokenModel(
            token="blacklist-token-b",
            user_id=user_m.id,
            expired_at=datetime.now(UTC),
            blacklisted=False,
        )
        session.add_all([token_a, token_b])
        await session.flush()

        repo = AccessTokenRepository(session)
        await repo.blacklist_all_for_user(user_m.id)

        stmt = select(AccessTokenModel).where(AccessTokenModel.user_id == user_m.id)
        result = await session.execute(stmt)
        tokens = result.scalars().all()
        assert len(tokens) == 2
        assert all(t.blacklisted for t in tokens)

    async def test_does_not_blacklist_other_users_tokens(
        self, session: AsyncSession
    ):
        user_a = UserModel(
            username="user-a",
            email="user-a@example.com",
            password_hash="hash",
        )
        user_b = UserModel(
            username="user-b",
            email="user-b@example.com",
            password_hash="hash",
        )
        session.add_all([user_a, user_b])
        await session.flush()

        token_for_a = AccessTokenModel(
            token="for-user-a",
            user_id=user_a.id,
            expired_at=datetime.now(UTC),
            blacklisted=False,
        )
        token_for_b = AccessTokenModel(
            token="for-user-b",
            user_id=user_b.id,
            expired_at=datetime.now(UTC),
            blacklisted=False,
        )
        session.add_all([token_for_a, token_for_b])
        await session.flush()

        repo = AccessTokenRepository(session)
        await repo.blacklist_all_for_user(user_a.id)

        stmt_b = select(AccessTokenModel).where(AccessTokenModel.id == token_for_b.id)
        result_b = await session.execute(stmt_b)
        assert result_b.scalar_one().blacklisted is False
