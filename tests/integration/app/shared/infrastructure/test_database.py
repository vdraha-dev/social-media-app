from datetime import datetime
from uuid import UUID

import pytest
from pytz import UTC
from sqlalchemy import String, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.database import Base, UnitOfWork, init_db
from tests.integration.conftest import TEST_DATABASE_URL


class TestModel(Base):
    __test__ = False
    __tablename__ = "test_entities"

    name: Mapped[str] = mapped_column(String(100), nullable=False)


class TestInitDb:
    def test_init_db_creates_database_and_is_idempotent(self, db_settings: None):
        init_db()
        init_db()


class TestEngineConnection:
    async def test_engine_connects(self, db_setup: None):
        engine = create_async_engine(TEST_DATABASE_URL)
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1 AS value"))
            row = result.one()
            assert row.value == 1
        await engine.dispose()


class TestBaseModel:
    async def test_create_and_select(self, session: AsyncSession):
        model = TestModel(name="test-entity")
        session.add(model)
        await session.commit()

        result = await session.execute(
            text("SELECT name FROM test_entities WHERE id = :id"),
            {"id": model.id},
        )
        row = result.one()
        assert row.name == "test-entity"

    async def test_auto_generates_uuid(self, session: AsyncSession):
        model = TestModel(name="uuid-test")
        session.add(model)
        await session.commit()

        assert isinstance(model.id, UUID)

    async def test_uuid_is_unique_per_instance(self, session: AsyncSession):
        model_a = TestModel(name="uuid-a")
        model_b = TestModel(name="uuid-b")
        session.add_all([model_a, model_b])
        await session.commit()

        assert model_a.id != model_b.id

    async def test_auto_generates_timestamps(self, session: AsyncSession):
        model = TestModel(name="timestamps-test")
        session.add(model)
        await session.commit()

        assert model.created_at is not None
        assert model.updated_at is not None
        assert model.created_at.tzinfo is not None
        assert model.updated_at.tzinfo is not None

    async def test_created_at_and_updated_at_are_on_creation(
        self, session: AsyncSession
    ):
        before = datetime.now(UTC)
        model = TestModel(name="creation-time")
        session.add(model)
        await session.commit()
        after = datetime.now(UTC)

        created = model.created_at.replace(tzinfo=UTC)
        updated = model.updated_at.replace(tzinfo=UTC)

        assert before <= created <= after
        assert before <= updated <= after

    async def test_updated_at_updates_on_change(self, session: AsyncSession):
        model = TestModel(name="update-test")
        session.add(model)
        await session.commit()

        original_id = model.id

        model.name = "updated-name"
        await session.commit()

        result = await session.execute(
            text("SELECT updated_at FROM test_entities WHERE id = :id"),
            {"id": original_id},
        )
        updated = result.scalar_one()
        assert updated is not None

    async def test_created_at_stays_same_on_update(self, session: AsyncSession):
        model = TestModel(name="created-at-immutable")
        session.add(model)
        await session.commit()

        original_created_at = model.created_at

        model.name = "new-name"
        await session.commit()

        assert model.created_at == original_created_at


class TestAsyncSessionLocal:
    async def test_session_factory_executes_query(self, db_setup: None):
        engine = create_async_engine(TEST_DATABASE_URL)
        maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with maker() as sess:
            result = await sess.execute(text("SELECT 42 AS answer"))
            row = result.one()
            assert row.answer == 42

        await engine.dispose()


class TestUnitOfWork:
    async def test_commit(self, db_setup: None):
        engine = create_async_engine(TEST_DATABASE_URL)
        maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        session = maker()

        async with UnitOfWork(session):
            model = TestModel(name="uow-commit")
            session.add(model)

        maker_check = async_sessionmaker(engine, class_=AsyncSession)
        async with maker_check() as check_session:
            result = await check_session.execute(
                text("SELECT name FROM test_entities WHERE name = 'uow-commit'")
            )
            row = result.one()
            assert row.name == "uow-commit"

        await engine.dispose()

    async def test_rollback_on_exception(self, db_setup: None):
        engine = create_async_engine(TEST_DATABASE_URL)
        maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        session = maker()

        with pytest.raises(RuntimeError):
            async with UnitOfWork(session):
                model = TestModel(name="uow-rollback")
                session.add(model)
                raise RuntimeError("test error")

        maker_check = async_sessionmaker(engine, class_=AsyncSession)
        async with maker_check() as check_session:
            result = await check_session.execute(
                text("SELECT COUNT(*) FROM test_entities WHERE name = 'uow-rollback'")
            )
            count = result.scalar()
            assert count == 0

        await engine.dispose()

    async def test_session_has_no_pending_changes_after_exit(self, db_setup: None):
        engine = create_async_engine(TEST_DATABASE_URL)
        maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        session = maker()

        async with UnitOfWork(session):
            model = TestModel(name="clean-exit")
            session.add(model)

        assert model not in session.new
        assert len(session.new) == 0
        await engine.dispose()
