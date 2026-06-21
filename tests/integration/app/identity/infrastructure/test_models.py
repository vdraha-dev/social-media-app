from datetime import datetime
from uuid import UUID

import pytest
from pytz import UTC
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.identity.domain.value_objects import HashedPassword, Role, UserName
from app.identity.infrastructure.models import AccessTokenModel, UserModel
from app.shared.domain.value_objects import Email


class TestUserModel:
    async def test_create_and_select(self, session: AsyncSession):
        user = UserModel(
            username=UserName("testuser"),
            email=Email("test@example.com"),
            password_hash=HashedPassword("hashed_pw"),
        )
        session.add(user)
        await session.commit()

        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await session.execute(stmt)
        loaded = result.scalar_one()
        assert loaded.username == UserName("testuser")
        assert loaded.email == Email("test@example.com")
        assert loaded.password_hash == HashedPassword("hashed_pw")
        assert loaded.role == Role()

    async def test_auto_generates_uuid(self, session: AsyncSession):
        user = UserModel(
            username=UserName("uuid-test"),
            email=Email("uuid-test@example.com"),
            password_hash=HashedPassword("hash"),
        )
        session.add(user)
        await session.commit()

        assert isinstance(user.id, UUID)

    async def test_uuid_is_unique_per_instance(self, session: AsyncSession):
        user_a = UserModel(
            username=UserName("uuid-a"),
            email=Email("uuid-a@example.com"),
            password_hash=HashedPassword("hash"),
        )
        user_b = UserModel(
            username=UserName("uuid-b"),
            email=Email("uuid-b@example.com"),
            password_hash=HashedPassword("hash"),
        )
        session.add_all([user_a, user_b])
        await session.commit()

        assert user_a.id != user_b.id

    async def test_auto_generates_timestamps(self, session: AsyncSession):
        user = UserModel(
            username=UserName("timestamps-test"),
            email=Email("timestamps-test@example.com"),
            password_hash=HashedPassword("hash"),
        )
        session.add(user)
        await session.commit()

        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.created_at.tzinfo is not None
        assert user.updated_at.tzinfo is not None

    async def test_created_at_and_updated_at_are_on_creation(
        self, session: AsyncSession
    ):
        before = datetime.now(UTC)
        user = UserModel(
            username=UserName("creation-time"),
            email=Email("creation-time@example.com"),
            password_hash=HashedPassword("hash"),
        )
        session.add(user)
        await session.commit()
        after = datetime.now(UTC)

        created = user.created_at.replace(tzinfo=UTC)
        updated = user.updated_at.replace(tzinfo=UTC)

        assert before <= created <= after
        assert before <= updated <= after

    async def test_updated_at_updates_on_change(self, session: AsyncSession):
        user = UserModel(
            username=UserName("update-test"),
            email=Email("update-test@example.com"),
            password_hash=HashedPassword("hash"),
        )
        session.add(user)
        await session.commit()

        original_id = user.id

        user.username = UserName("updated-username")
        await session.commit()

        result = await session.execute(
            text("SELECT updated_at FROM users WHERE id = :id"),
            {"id": original_id},
        )
        updated = result.scalar_one()
        assert updated is not None

    async def test_created_at_stays_same_on_update(self, session: AsyncSession):
        user = UserModel(
            username=UserName("created-at-test"),
            email=Email("created-at-test@example.com"),
            password_hash=HashedPassword("hash"),
        )
        session.add(user)
        await session.commit()

        original_created_at = user.created_at

        user.username = UserName("new-username")
        await session.commit()

        assert user.created_at == original_created_at

    async def test_default_role_is_user(self, session: AsyncSession):
        user = UserModel(
            username=UserName("role-test"),
            email=Email("role-test@example.com"),
            password_hash=HashedPassword("hash"),
        )
        session.add(user)
        await session.commit()

        assert user.role == Role()

    async def test_email_uniqueness_constraint(self, session: AsyncSession):
        user = UserModel(
            username=UserName("first"),
            email=Email("duplicate@example.com"),
            password_hash=HashedPassword("hash"),
        )
        session.add(user)
        await session.commit()

        duplicate = UserModel(
            username=UserName("second"),
            email=Email("duplicate@example.com"),
            password_hash=HashedPassword("hash"),
        )
        session.add(duplicate)
        with pytest.raises(IntegrityError):
            await session.commit()

    async def test_nullable_last_login(self, session: AsyncSession):
        user = UserModel(
            username=UserName("last-login-test"),
            email=Email("last-login-test@example.com"),
            password_hash=HashedPassword("hash"),
        )
        session.add(user)
        await session.commit()

        assert user.last_login is None


class TestAccessTokenModel:
    async def test_create_and_select(self, session: AsyncSession):
        user = UserModel(
            username=UserName("token-user"),
            email=Email("token-user@example.com"),
            password_hash=HashedPassword("hash"),
        )
        session.add(user)
        await session.commit()

        access_token = AccessTokenModel(
            token="test-token-123",
            user_id=user.id,
            expired_at=datetime.now(UTC),
            blacklisted=False,
        )
        session.add(access_token)
        await session.commit()

        result = await session.execute(
            text(
                "SELECT token, user_id, expired_at, blacklisted "
                "FROM access_tokens WHERE id = :id"
            ),
            {"id": access_token.id},
        )
        row = result.one()
        assert row.token == "test-token-123"
        assert row.user_id == user.id
        assert row.blacklisted is False

    async def test_auto_generates_uuid(self, session: AsyncSession):
        user = UserModel(
            username=UserName("uuid-token-user"),
            email=Email("uuid-token-user@example.com"),
            password_hash=HashedPassword("hash"),
        )
        session.add(user)
        await session.commit()

        access_token = AccessTokenModel(
            token="uuid-test-token",
            user_id=user.id,
            expired_at=datetime.now(UTC),
            blacklisted=False,
        )
        session.add(access_token)
        await session.commit()

        assert isinstance(access_token.id, UUID)

    async def test_uuid_is_unique_per_instance(self, session: AsyncSession):
        user = UserModel(
            username=UserName("unique-uuid-user"),
            email=Email("unique-uuid-user@example.com"),
            password_hash=HashedPassword("hash"),
        )
        session.add(user)
        await session.commit()

        token_a = AccessTokenModel(
            token="unique-token-a",
            user_id=user.id,
            expired_at=datetime.now(UTC),
            blacklisted=False,
        )
        token_b = AccessTokenModel(
            token="unique-token-b",
            user_id=user.id,
            expired_at=datetime.now(UTC),
            blacklisted=False,
        )
        session.add_all([token_a, token_b])
        await session.commit()

        assert token_a.id != token_b.id

    async def test_auto_generates_timestamps(self, session: AsyncSession):
        user = UserModel(
            username=UserName("timestamps-token-user"),
            email=Email("timestamps-token-user@example.com"),
            password_hash=HashedPassword("hash"),
        )
        session.add(user)
        await session.commit()

        access_token = AccessTokenModel(
            token="timestamps-test-token",
            user_id=user.id,
            expired_at=datetime.now(UTC),
            blacklisted=False,
        )
        session.add(access_token)
        await session.commit()
        assert access_token.created_at is not None
        assert access_token.updated_at is not None
        assert access_token.created_at.tzinfo is not None
        assert access_token.updated_at.tzinfo is not None

    async def test_foreign_key_constraint(self, session: AsyncSession):
        fake_user_id = UUID("00000000-0000-0000-0000-000000000000")
        access_token = AccessTokenModel(
            token="fk-test-token",
            user_id=fake_user_id,
            expired_at=datetime.now(UTC),
            blacklisted=False,
        )
        session.add(access_token)
        with pytest.raises(IntegrityError):
            await session.commit()

    async def test_token_uniqueness(self, session: AsyncSession):
        user = UserModel(
            username=UserName("token-unique-user"),
            email=Email("token-unique-user@example.com"),
            password_hash=HashedPassword("hash"),
        )
        session.add(user)
        await session.commit()

        first = AccessTokenModel(
            token="same-token",
            user_id=user.id,
            expired_at=datetime.now(UTC),
            blacklisted=False,
        )
        session.add(first)
        await session.commit()

        second = AccessTokenModel(
            token="same-token",
            user_id=user.id,
            expired_at=datetime.now(UTC),
            blacklisted=False,
        )
        session.add(second)
        with pytest.raises(IntegrityError):
            await session.commit()


class TestUserAccessTokenRelationship:
    async def test_user_has_tokens(self, session: AsyncSession):
        user = UserModel(
            username=UserName("rel-user"),
            email=Email("rel-user@example.com"),
            password_hash=HashedPassword("hash"),
        )
        session.add(user)
        await session.commit()

        token = AccessTokenModel(
            token="rel-token",
            user_id=user.id,
            expired_at=datetime.now(UTC),
            blacklisted=False,
        )
        session.add(token)
        await session.commit()

        stmt = (
            select(UserModel)
            .where(UserModel.id == user.id)
            .options(selectinload(UserModel.tokens))
        )
        result = await session.execute(stmt)
        loaded = result.scalar_one()
        assert len(loaded.tokens) == 1
        assert loaded.tokens[0].token == "rel-token"

    async def test_token_belongs_to_user(self, session: AsyncSession):
        user = UserModel(
            username=UserName("belongs-user"),
            email=Email("belongs-user@example.com"),
            password_hash=HashedPassword("hash"),
        )
        session.add(user)
        await session.commit()

        token = AccessTokenModel(
            token="belongs-token",
            user_id=user.id,
            expired_at=datetime.now(UTC),
            blacklisted=False,
        )
        session.add(token)
        await session.commit()

        assert token.user.id == user.id
        assert token.user.username == UserName("belongs-user")

    async def test_cascade_delete_from_user(self, session: AsyncSession):
        user = UserModel(
            username=UserName("cascade-user"),
            email=Email("cascade-user@example.com"),
            password_hash=HashedPassword("hash"),
        )
        session.add(user)
        await session.commit()

        token = AccessTokenModel(
            token="cascade-token",
            user_id=user.id,
            expired_at=datetime.now(UTC),
            blacklisted=False,
        )
        session.add(token)
        await session.commit()

        token_id = token.id
        await session.delete(user)
        await session.commit()

        result = await session.execute(
            text("SELECT COUNT(*) FROM access_tokens WHERE id = :id"),
            {"id": token_id},
        )
        count = result.scalar()
        assert count == 0
