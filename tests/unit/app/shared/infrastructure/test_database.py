from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.shared.infrastructure.database import (
    AsyncSessionLocal,
    Base,
    UnitOfWork,
    get_session,
    get_uow,
    init_db,
)


class TestUnitOfWork:
    @pytest.mark.asyncio
    async def test_aenter_returns_self(self):
        session = AsyncMock()
        uow = UnitOfWork(session)
        result = await uow.__aenter__()
        assert result is uow

    @pytest.mark.asyncio
    async def test_aexit_no_exception_commits(self):
        session = AsyncMock()
        uow = UnitOfWork(session)
        await uow.__aexit__(None, None, None)
        session.commit.assert_awaited_once()
        session.close.assert_awaited_once()
        session.rollback.assert_not_called()

    @pytest.mark.asyncio
    async def test_aexit_with_exception_rolls_back(self):
        session = AsyncMock()
        uow = UnitOfWork(session)
        exc = ValueError("test error")
        await uow.__aexit__(type(exc), exc, None)
        session.rollback.assert_awaited_once()
        session.close.assert_awaited_once()
        session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_commit_delegates(self):
        session = AsyncMock()
        uow = UnitOfWork(session)
        await uow.commit()
        session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_rollback_delegates(self):
        session = AsyncMock()
        uow = UnitOfWork(session)
        await uow.rollback()
        session.rollback.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_close_on_exit(self):
        session = AsyncMock()
        uow = UnitOfWork(session)
        await uow.__aexit__(None, None, None)
        session.close.assert_awaited_once()


class TestBase:
    def test_has_id_column(self):
        assert hasattr(Base, "id")

    def test_has_created_at_column(self):
        assert hasattr(Base, "created_at")

    def test_has_updated_at_column(self):
        assert hasattr(Base, "updated_at")


class TestInitDb:
    @patch("app.shared.infrastructure.database.create_engine")
    @patch("app.shared.infrastructure.database.settings")
    def test_init_db_when_db_exists(self, mock_settings, mock_create_engine):
        mock_settings.SYNC_DATABASE_URL = "postgresql://localhost/testdb"
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value.scalar_one_or_none.return_value = 1

        init_db()

        mock_create_engine.assert_called()
        mock_conn.execute.assert_called()
        mock_conn.execute.return_value.scalar_one_or_none.assert_called_once()
        assert mock_conn.execute.call_count == 1

    @patch("app.shared.infrastructure.database.create_engine")
    @patch("app.shared.infrastructure.database.settings")
    def test_init_db_creates_when_not_exists(self, mock_settings, mock_create_engine):
        mock_settings.SYNC_DATABASE_URL = "postgresql://localhost/testdb"
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value.scalar_one_or_none.return_value = None

        init_db()

        assert mock_conn.execute.call_count == 2

    @patch("app.shared.infrastructure.database.create_engine")
    @patch("app.shared.infrastructure.database.settings")
    def test_init_db_parses_url_correctly(self, mock_settings, mock_create_engine):
        mock_settings.SYNC_DATABASE_URL = "postgresql://user:pass@host:5432/mydb"
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value.scalar_one_or_none.return_value = 1

        init_db()

        admin_url = mock_create_engine.call_args[0][0]
        assert admin_url == "postgresql://user:pass@host:5432/postgres"


class TestGetSession:
    @pytest.mark.asyncio
    async def test_get_session_yields_async_session(self):
        from sqlalchemy.ext.asyncio import AsyncSession

        gen = get_session()
        session = await gen.__anext__()
        assert isinstance(session, AsyncSession)
        await gen.aclose()


class TestGetUow:
    @pytest.mark.asyncio
    async def test_get_uow_yields(self):
        mock_session = AsyncMock()
        mock_uow = MagicMock()

        with (
            patch.object(AsyncSessionLocal, "__call__", return_value=mock_session),
            patch(
                "app.shared.infrastructure.database.UnitOfWork",
                return_value=mock_uow,
            ),
        ):
            mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
            mock_uow.__aexit__ = AsyncMock(return_value=None)

            gen = get_uow()
            uow = await gen.__anext__()
            assert uow is mock_uow
            with pytest.raises(StopAsyncIteration):
                await gen.__anext__()
