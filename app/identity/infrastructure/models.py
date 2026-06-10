from datetime import datetime
from uuid import UUID

from click import DateTime
from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.identity.domain.value_objects import RoleEnum
from app.shared.infrastructure.database import Base


class UserModel(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[RoleEnum] = mapped_column(SqlEnum(RoleEnum), default=RoleEnum.User)
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # relationships

    tokens: Mapped[list[AccessToken]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class AccessTokenModel(Base):
    __tablename__ = "access_tokens"

    token: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    expire_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    blacklisted: Mapped[bool] = mapped_column(Boolean)

    # relationships

    user: Mapped[UserModel] = relationship(back_populates="tokens")
