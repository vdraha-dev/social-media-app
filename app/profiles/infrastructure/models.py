from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.database import Base


class UserProfileModel(Base):
    user_id: Mapped[UUID] = mapped_column(
        PUUID(as_uuid=True), ForeignKey("users.id"), unique=True
    )
    displayed_name: Mapped[str] = mapped_column(String(100), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    bio: Mapped[str | None] = mapped_column(String(500), nullable=True)
    social_links: Mapped[list[str]] = mapped_column(
        ARRAY(String(512)), default=list, nullable=False
    )
