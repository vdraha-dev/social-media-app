from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from pytz import UTC

from app.identity.domain.entities import AccessToken, User
from app.identity.domain.value_objects import HashedPassword, Role, RoleEnum, UserName
from app.identity.infrastructure.models import AccessTokenModel, UserModel
from app.identity.infrastructure.repository import AccessTokenRepository, UserRepository
from app.shared.domain.value_objects import Email
from app.shared.utils import uuid_gen


class TestUserRepositoryGetUserById:
    async def test_returns_user_when_found(self):
        session = MagicMock(spec=AsyncMock)
        session.get = AsyncMock(
            return_value=UserModel(
                id=uuid_gen(),
                username="alice",
                email="alice@example.com",
                password_hash="hash",
                role=RoleEnum.User,
                last_login=None,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
        )
        repo = UserRepository(session)
        uid = uuid_gen()

        result = await repo.get_user_by_id(uid)

        assert isinstance(result, User)
        session.get.assert_awaited_once_with(UserModel, uid)

    async def test_returns_none_when_not_found(self):
        session = MagicMock(spec=AsyncMock)
        session.get = AsyncMock(return_value=None)
        repo = UserRepository(session)

        result = await repo.get_user_by_id(uuid_gen())

        assert result is None


class TestUserRepositoryGetByEmail:
    async def test_returns_user_when_found(self):
        session = MagicMock(spec=AsyncMock)
        scalar = MagicMock()
        scalar.scalar_one_or_none = MagicMock(
            return_value=UserModel(
                id=uuid_gen(),
                username="bob",
                email="bob@example.com",
                password_hash="hash",
                role=RoleEnum.User,
                last_login=None,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
        )
        session.execute = AsyncMock(return_value=scalar)
        repo = UserRepository(session)
        email = Email(value="bob@example.com")

        result = await repo.get_by_email(email)

        assert isinstance(result, User)
        session.execute.assert_awaited_once()

    async def test_returns_none_when_not_found(self):
        session = MagicMock(spec=AsyncMock)
        scalar = MagicMock()
        scalar.scalar_one_or_none = MagicMock(return_value=None)
        session.execute = AsyncMock(return_value=scalar)
        repo = UserRepository(session)

        result = await repo.get_by_email(Email(value="nobody@example.com"))

        assert result is None


class TestUserRepositorySave:
    async def test_inserts_new_user(self):
        session = MagicMock(spec=AsyncMock)
        session.get = AsyncMock(return_value=None)
        session.add = MagicMock()
        session.flush = AsyncMock()
        repo = UserRepository(session)
        user = User(
            username=UserName(value="charlie"),
            email=Email(value="charlie@example.com"),
            password=HashedPassword(value="hash"),
            role=Role(),
        )

        await repo.save(user)

        session.get.assert_awaited_once_with(UserModel, user.id)
        session.add.assert_called_once()
        session.flush.assert_awaited_once()

    async def test_updates_existing_user(self):
        user_id = uuid_gen()
        existing = UserModel(
            id=user_id,
            username="old",
            email="old@example.com",
            password_hash="old_hash",
            role=RoleEnum.User,
            last_login=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        session = MagicMock(spec=AsyncMock)
        session.get = AsyncMock(return_value=existing)
        session.flush = AsyncMock()
        repo = UserRepository(session)
        user = User(
            username=UserName(value="new"),
            email=Email(value="new@example.com"),
            password=HashedPassword(value="new_hash"),
            role=Role(),
            id=user_id,
        )

        await repo.save(user)

        assert existing.username == "new"
        assert existing.email == "new@example.com"
        assert existing.password_hash == "new_hash"
        session.get.assert_awaited_once_with(UserModel, user_id)
        session.flush.assert_awaited_once()


class TestUserRepositoryExistsByEmail:
    async def test_returns_true_when_exists(self):
        session = MagicMock(spec=AsyncMock)
        scalar = MagicMock()
        scalar.scalar_one_or_none = MagicMock(return_value=MagicMock())
        session.execute = AsyncMock(return_value=scalar)
        repo = UserRepository(session)

        result = await repo.exists_by_email(Email(value="exists@example.com"))

        assert result is True

    async def test_returns_false_when_not_exists(self):
        session = MagicMock(spec=AsyncMock)
        scalar = MagicMock()
        scalar.scalar_one_or_none = MagicMock(return_value=None)
        session.execute = AsyncMock(return_value=scalar)
        repo = UserRepository(session)

        result = await repo.exists_by_email(Email(value="missing@example.com"))

        assert result is False


class TestUserRepositoryToEntity:
    def test_maps_all_fields(self):
        uid = uuid_gen()
        now = datetime.now(UTC)
        model = UserModel(
            id=uid,
            username="alice",
            email="alice@example.com",
            password_hash="hash",
            role=RoleEnum.User,
            last_login=now,
            created_at=now,
            updated_at=now,
        )
        repo = UserRepository(MagicMock())

        entity = repo._to_entity(model)  # pyright: ignore

        assert entity.id == uid
        assert entity.username == UserName(value="alice")
        assert entity.email == Email(value="alice@example.com")
        assert entity.password == HashedPassword(value="hash")
        assert entity.role.value == RoleEnum.User
        assert entity.last_login == now
        assert entity.created_at == now
        assert entity.updated_at == now

    def test_maps_none_last_login(self):
        model = UserModel(
            id=uuid_gen(),
            username="alice",
            email="alice@example.com",
            password_hash="hash",
            role=RoleEnum.User,
            last_login=None,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        repo = UserRepository(MagicMock())

        entity = repo._to_entity(model)  # pyright: ignore

        assert entity.last_login is None


class TestUserRepositoryToModel:
    def test_maps_all_fields(self):
        uid = uuid_gen()
        now = datetime.now(UTC)
        entity = User(
            username=UserName(value="alice"),
            email=Email(value="alice@example.com"),
            password=HashedPassword(value="hash"),
            role=Role(),
            last_login=now,
            id=uid,
            created_at=now,
            updated_at=now,
        )
        repo = UserRepository(MagicMock())

        model = repo._to_model(entity)  # pyright: ignore

        assert model.id == uid
        assert model.username == "alice"
        assert model.email == "alice@example.com"
        assert model.password_hash == "hash"
        assert model.role == RoleEnum.User
        assert model.last_login == now
        assert model.created_at == now
        assert model.updated_at == now


class TestAccessTokenRepositoryGetByToken:
    async def test_returns_token_when_found(self):
        session = MagicMock(spec=AsyncMock)
        uid = uuid_gen()
        now = datetime.now(UTC)
        scalar = MagicMock()
        scalar.scalar_one_or_none = MagicMock(
            return_value=AccessTokenModel(
                id=uuid_gen(),
                token="token-123",
                user_id=uid,
                expired_at=now,
                blacklisted=False,
                created_at=now,
                updated_at=now,
            )
        )
        session.execute = AsyncMock(return_value=scalar)
        repo = AccessTokenRepository(session)

        result = await repo.get_by_token("token-123")

        assert isinstance(result, AccessToken)
        session.execute.assert_awaited_once()

    async def test_returns_none_when_not_found(self):
        session = MagicMock(spec=AsyncMock)
        scalar = MagicMock()
        scalar.scalar_one_or_none = MagicMock(return_value=None)
        session.execute = AsyncMock(return_value=scalar)
        repo = AccessTokenRepository(session)

        result = await repo.get_by_token("unknown-token")

        assert result is None


class TestAccessTokenRepositorySave:
    async def test_adds_and_flushes(self):
        session = MagicMock(spec=AsyncMock)
        session.add = MagicMock()
        session.flush = AsyncMock()
        repo = AccessTokenRepository(session)
        token = AccessToken(
            token="token-123",
            user_id=uuid_gen(),
            expired_at=datetime.now(UTC),
        )

        await repo.save(token)

        session.add.assert_called_once()
        session.flush.assert_awaited_once()


class TestAccessTokenRepositoryBlacklistAllForUser:
    async def test_executes_update(self):
        session = MagicMock(spec=AsyncMock)
        session.execute = AsyncMock()
        repo = AccessTokenRepository(session)
        uid = uuid_gen()

        await repo.blacklist_all_for_user(uid)

        session.execute.assert_awaited_once()


class TestAccessTokenRepositoryToModel:
    def test_maps_all_fields(self):
        uid = uuid_gen()
        now = datetime.now(UTC)
        entity = AccessToken(
            token="token-123",
            user_id=uid,
            expired_at=now,
            blacklisted=True,
            id=uid,
            created_at=now,
            updated_at=now,
        )
        repo = AccessTokenRepository(MagicMock())

        model = repo._to_model(entity)  # pyright: ignore

        assert model.id == uid
        assert model.token == "token-123"
        assert model.user_id == uid
        assert model.expired_at == now
        assert model.blacklisted is True
        assert model.created_at == now
        assert model.updated_at == now


class TestAccessTokenRepositoryToEntity:
    def test_maps_all_fields(self):
        uid = uuid_gen()
        now = datetime.now(UTC)
        model = AccessTokenModel(
            id=uid,
            token="token-123",
            user_id=uid,
            expired_at=now,
            blacklisted=True,
            created_at=now,
            updated_at=now,
        )
        repo = AccessTokenRepository(MagicMock())

        entity = repo._to_entity(model)  # pyright: ignore

        assert entity.id == uid
        assert entity.token == "token-123"
        assert entity.user_id == uid
        assert entity.expired_at == now
        assert entity.blacklisted is True
        assert entity.created_at == now
        assert entity.updated_at == now
