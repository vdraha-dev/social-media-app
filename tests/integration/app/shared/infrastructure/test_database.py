from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.infrastructure.database import (
    Base,
    UnitOfWork,
    get_session,
    get_uow,
)


class TestUnitOfWorkTransaction:
    @pytest.mark.asyncio
    async def test_aenter_returns_uow(self):
        session = AsyncMock(spec=AsyncSession)
        uow = UnitOfWork(session)
        result = await uow.__aenter__()
        assert result is uow

    @pytest.mark.asyncio
    async def test_exit_commits_on_success(self):
        session = AsyncMock(spec=AsyncSession)
        uow = UnitOfWork(session)
        await uow.__aexit__(None, None, None)
        session.commit.assert_awaited_once()
        session.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_exit_rolls_back_on_error(self):
        session = AsyncMock(spec=AsyncSession)
        uow = UnitOfWork(session)
        await uow.__aexit__(ValueError, ValueError("err"), None)
        session.rollback.assert_awaited_once()
        session.close.assert_awaited_once()
        session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_commit_and_rollback_delegate_to_session(self):
        session = AsyncMock(spec=AsyncSession)
        uow = UnitOfWork(session)

        await uow.commit()
        session.commit.assert_awaited_once()

        await uow.rollback()
        session.rollback.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_context_manager_commit_on_success(self):
        session = AsyncMock(spec=AsyncSession)
        async with UnitOfWork(session):
            pass
        session.commit.assert_awaited_once()
        session.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_context_manager_rollback_on_error(self):
        session = AsyncMock(spec=AsyncSession)
        with pytest.raises(RuntimeError):
            async with UnitOfWork(session):
                raise RuntimeError("fail")
        session.rollback.assert_awaited_once()
        session.close.assert_awaited_once()


class TestBaseModel:
    def test_base_has_id_column(self):
        assert hasattr(Base, "id")

    def test_base_has_created_at_column(self):
        assert hasattr(Base, "created_at")

    def test_base_has_updated_at_column(self):
        assert hasattr(Base, "updated_at")

    def test_tablename_not_set_on_base(self):
        assert not hasattr(Base, "__tablename__")


class TestGetSession:
    @pytest.mark.asyncio
    async def test_get_session_yields_async_session(self):
        gen = get_session()
        session = await gen.__anext__()
        assert isinstance(session, AsyncSession)
        await gen.aclose()


class TestGetUow:
    @pytest.mark.asyncio
    async def test_get_uow_yields(self):
        gen = get_uow()
        try:
            await gen.__anext__()
        except StopAsyncIteration:
            pass
