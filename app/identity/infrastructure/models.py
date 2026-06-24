from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.identity.domain.value_objects import HashedPassword, Role, UserName
from app.identity.infrastructure.types import HashedPasswordType, RoleType, UserNameType
from app.shared.domain.value_objects import Email
from app.shared.infrastructure.database import Base
from app.shared.infrastructure.types import EmailType


class UserModel(Base):
    __tablename__ = "users"

    username: Mapped[UserName] = mapped_column(UserNameType(), nullable=False)
    email: Mapped[Email] = mapped_column(EmailType(), unique=True, nullable=False)
    password_hash: Mapped[HashedPassword] = mapped_column(
        HashedPasswordType(), nullable=False
    )
    role: Mapped[Role] = mapped_column(RoleType(), default=Role)
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # relationships

    tokens: Mapped[list[AccessTokenModel]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class AccessTokenModel(Base):
    __tablename__ = "access_tokens"

    token: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    user_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("users.id"))
    expired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    blacklisted: Mapped[bool] = mapped_column(Boolean)

    # relationships

    user: Mapped[UserModel] = relationship(back_populates="tokens")
