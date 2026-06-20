from os import environ

import pytest
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.shared.infrastructure.database import Base

TEST_DATABASE_URL = environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/appdb_test",
)
TEST_SYNC_DATABASE_URL = environ.get(
    "TEST_SYNC_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/appdb_test",
)


@pytest.fixture(scope="session")
def db_settings():
    from app.shared.config import settings

    original_url = settings.DATABASE_URL
    original_sync_url = settings.SYNC_DATABASE_URL

    settings.DATABASE_URL = TEST_DATABASE_URL
    settings.SYNC_DATABASE_URL = TEST_SYNC_DATABASE_URL

    yield

    settings.DATABASE_URL = original_url
    settings.SYNC_DATABASE_URL = original_sync_url


def _truncate_all(engine: Engine):
    with engine.begin() as conn:
        result = conn.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        )
        tables = [row[0] for row in result]
        if tables:
            table_list = ", ".join(f'"{t}"' for t in tables)
            conn.execute(text(f"TRUNCATE TABLE {table_list} CASCADE"))


@pytest.fixture(scope="function")
def db_setup(db_settings: None):
    from app.shared.infrastructure.database import init_db

    init_db()

    sync_engine = create_engine(TEST_SYNC_DATABASE_URL)
    Base.metadata.create_all(sync_engine)
    _truncate_all(sync_engine)
    sync_engine.dispose()

    yield

    clean_engine = create_engine(TEST_SYNC_DATABASE_URL)
    _truncate_all(clean_engine)
    clean_engine.dispose()


@pytest.fixture
async def session(db_setup: None):
    engine = create_async_engine(TEST_DATABASE_URL, pool_size=1, max_overflow=0)

    maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    sess = maker()
    yield sess
    await sess.rollback()
    await sess.close()
    await engine.dispose()
