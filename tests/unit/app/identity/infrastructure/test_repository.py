from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.identity.domain.value_objects import RoleEnum
from app.identity.infrastructure.repository import (
    AccessTokenRepository,
    UserRepository,
)


class TestUserRepository:
    @pytest.fixture
    def session(self):
        return AsyncMock()

    @pytest.fixture
    def repo(self, session):
        return UserRepository(session)

    def test_init(self, repo, session):
        assert repo.session is session

    @pytest.mark.asyncio
    async def test_get_user_by_id_returns_none(self, repo, session):
        session.get = AsyncMock(return_value=None)
        result = await repo.get_user_by_id(uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_by_id_returns_user(self, repo, session):
        mock_model = MagicMock()
        mock_model.id = uuid4()
        mock_model.username = "testuser"
        mock_model.email = "test@example.com"
        mock_model.password_hash = "hash"
        mock_model.role = RoleEnum.User
        mock_model.last_login = None
        mock_model.created_at = MagicMock()
        mock_model.updated_at = MagicMock()
        session.get = AsyncMock(return_value=mock_model)

        result = await repo.get_user_by_id(mock_model.id)
        assert result is not None
        assert str(result.username) == "testuser"

    @pytest.mark.asyncio
    async def test_get_by_email_returns_none(self, repo, session):
        mock_execute = MagicMock()
        mock_execute.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=mock_execute)

        result = await repo.get_by_email("missing@example.com")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_email_returns_user(self, repo, session):
        mock_model = MagicMock()
        mock_model.id = uuid4()
        mock_model.username = "testuser"
        mock_model.email = "test@example.com"
        mock_model.password_hash = "hash"
        mock_model.role = RoleEnum.User
        mock_model.last_login = None
        mock_model.created_at = MagicMock()
        mock_model.updated_at = MagicMock()

        mock_execute = MagicMock()
        mock_execute.scalar_one_or_none.return_value = mock_model
        session.execute = AsyncMock(return_value=mock_execute)

        result = await repo.get_by_email("test@example.com")
        assert result is not None

    @pytest.mark.asyncio
    async def test_save_new_user(self, repo, session, monkeypatch):
        user = MagicMock()
        user.id = uuid4()
        user.username = MagicMock()
        user.email = MagicMock()
        user.password = MagicMock()
        user.role = MagicMock()
        user.last_login = None
        user.created_at = MagicMock()
        user.updated_at = MagicMock()

        session.get = AsyncMock(return_value=None)

        await repo.save(user)
        session.add.assert_called_once()
        session.flush.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_save_existing_user(self, repo, session):
        existing_model = MagicMock()
        session.get = AsyncMock(return_value=existing_model)

        user = MagicMock()
        user.id = uuid4()
        user.username = MagicMock()
        user.email = str
        user.password = MagicMock()
        user.role = MagicMock()
        user.last_login = None
        user.updated_at = MagicMock()

        await repo.save(user)
        session.add.assert_not_called()
        session.flush.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_exists_by_email_returns_true(self, repo, session):
        mock_execute = MagicMock()
        mock_execute.scalar_one_or_none.return_value = MagicMock()
        session.execute = AsyncMock(return_value=mock_execute)

        result = await repo.exists_by_email("exists@example.com")
        assert result is True

    @pytest.mark.asyncio
    async def test_exists_by_email_returns_false(self, repo, session):
        mock_execute = MagicMock()
        mock_execute.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=mock_execute)

        result = await repo.exists_by_email("missing@example.com")
        assert result is False


class TestAccessTokenRepository:
    @pytest.fixture
    def session(self):
        return AsyncMock()

    @pytest.fixture
    def repo(self, session):
        return AccessTokenRepository(session)

    def test_init(self, repo, session):
        assert repo.session is session

    @pytest.mark.asyncio
    async def test_get_by_token_returns_none(self, repo, session):
        mock_execute = MagicMock()
        mock_execute.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=mock_execute)

        result = await repo.get_by_token("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_token_returns_token(self, repo, session):
        mock_model = MagicMock()
        mock_model.id = uuid4()
        mock_model.token = "valid_token"
        mock_model.user_id = uuid4()
        mock_model.expired_at = MagicMock()
        mock_model.blacklisted = False
        mock_model.created_at = MagicMock()
        mock_model.updated_at = MagicMock()

        mock_execute = MagicMock()
        mock_execute.scalar_one_or_none.return_value = mock_model
        session.execute = AsyncMock(return_value=mock_execute)

        result = await repo.get_by_token("valid_token")
        assert result is not None
        assert result.token == "valid_token"

    @pytest.mark.asyncio
    async def test_save_adds_model(self, repo, session):
        token = MagicMock()
        token.id = uuid4()
        token.created_at = MagicMock()
        token.updated_at = MagicMock()
        token.token = "tok"
        token.user_id = uuid4()
        token.expired_at = MagicMock()
        token.blacklisted = False

        await repo.save(token)
        session.add.assert_called_once()
        session.flush.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_blacklist_all_for_user(self, repo, session):
        from sqlalchemy.sql.expression import Update

        user_id = uuid4()
        await repo.blacklist_all_for_user(user_id)

        session.execute.assert_awaited_once()
        call_stmt = session.execute.call_args[0][0]
        assert isinstance(call_stmt, Update)
