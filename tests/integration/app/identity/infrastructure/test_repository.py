from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from pytz import UTC

from app.identity.domain.entities import AccessToken, User
from app.identity.domain.value_objects import HashedPassword, Role, RoleEnum, UserName
from app.identity.infrastructure.models import AccessTokenModel, UserModel
from app.identity.infrastructure.repository import (
    AccessTokenRepository,
    UserRepository,
)
from app.shared.domain.value_objects import Email


class TestUserRepositoryMapping:
    def test_to_entity_maps_all_fields(self):
        model = MagicMock(spec=UserModel)
        model.id = uid = uuid4()
        model.username = "testuser"
        model.email = "test@example.com"
        model.password_hash = "hashed_value"
        model.role = RoleEnum.User
        model.last_login = now = datetime.now(UTC)
        model.created_at = now
        model.updated_at = now

        repo = UserRepository(AsyncMock())
        entity = repo._to_entity(model)

        assert entity.id == uid
        assert str(entity.username) == "testuser"
        assert str(entity.email) == "test@example.com"
        assert entity.password.value == "hashed_value"
        assert entity.role.value == RoleEnum.User
        assert entity.last_login == now

    def test_to_model_maps_all_fields(self):
        uid = uuid4()
        now = datetime.now(UTC)
        entity = User(
            username=UserName("testuser"),
            email=Email("test@example.com"),
            password=HashedPassword("hashed_value"),
            role=Role(),
            last_login=now,
        )
        entity.id = uid
        entity.created_at = now
        entity.updated_at = now

        repo = UserRepository(AsyncMock())
        model = repo._to_model(entity)

        assert model.id == uid
        assert model.username == "testuser"
        assert model.email == "test@example.com"
        assert model.password_hash == "hashed_value"
        assert model.role == RoleEnum.User
        assert model.last_login == now


class TestAccessTokenRepositoryMapping:
    def test_to_entity_maps_all_fields(self):
        model = MagicMock(spec=AccessTokenModel)
        model.id = uid = uuid4()
        model.token = "jwt_string"
        model.user_id = uuid4()
        model.expired_at = datetime.now(UTC) + timedelta(hours=1)
        model.blacklisted = False
        model.created_at = now = datetime.now(UTC)
        model.updated_at = now

        repo = AccessTokenRepository(AsyncMock())
        entity = repo._to_entity(model)

        assert entity.id == uid
        assert entity.token == "jwt_string"
        assert entity.user_id == model.user_id
        assert not entity.blacklisted

    def test_to_model_maps_all_fields(self):
        uid = uuid4()
        now = datetime.now(UTC)
        entity = AccessToken(
            token="jwt_string",
            user_id=uuid4(),
            expired_at=now + timedelta(hours=1),
            blacklisted=False,
        )
        entity.id = uid
        entity.created_at = now
        entity.updated_at = now

        repo = AccessTokenRepository(AsyncMock())
        model = repo._to_model(entity)

        assert model.id == uid
        assert model.token == "jwt_string"
        assert model.user_id == entity.user_id
        assert not model.blacklisted


class TestUserRepositoryQueries:
    @pytest.mark.asyncio
    async def test_get_user_by_id_returns_none(self):
        session = AsyncMock()
        session.get = AsyncMock(return_value=None)
        repo = UserRepository(session)

        result = await repo.get_user_by_id(uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_exists_by_email_returns_true(self):
        session = AsyncMock()
        mock_execute = MagicMock()
        mock_execute.scalar_one_or_none.return_value = MagicMock()
        session.execute = AsyncMock(return_value=mock_execute)
        repo = UserRepository(session)

        result = await repo.exists_by_email("exists@example.com")
        assert result

    @pytest.mark.asyncio
    async def test_exists_by_email_returns_false(self):
        session = AsyncMock()
        mock_execute = MagicMock()
        mock_execute.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=mock_execute)
        repo = UserRepository(session)

        result = await repo.exists_by_email("missing@example.com")
        assert not result


class TestAccessTokenRepositoryQueries:
    @pytest.mark.asyncio
    async def test_get_by_token_returns_none(self):
        session = AsyncMock()
        mock_execute = MagicMock()
        mock_execute.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=mock_execute)
        repo = AccessTokenRepository(session)

        result = await repo.get_by_token("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_blacklist_all_for_user_executes_update(self):
        session = AsyncMock()
        repo = AccessTokenRepository(session)
        user_id = uuid4()

        await repo.blacklist_all_for_user(user_id)
        session.execute.assert_awaited_once()
