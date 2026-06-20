from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.profiles.domain.value_objects import Bio, DisplayedName, SocialLink
from app.profiles.infrastructure.types import BioType, DisplayedNameType, SocialLinkType
from app.shared.domain.value_objects import Url
from app.shared.infrastructure.database import Base
from app.shared.infrastructure.types import UrlType


class UserProfileModel(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[UUID] = mapped_column(
        PUUID(as_uuid=True), ForeignKey("users.id"), unique=True
    )
    displayed_name: Mapped[DisplayedName] = mapped_column(
        DisplayedNameType(), nullable=False
    )
    avatar_url: Mapped[Url | None] = mapped_column(UrlType, nullable=True)
    bio: Mapped[Bio | None] = mapped_column(BioType, nullable=True)
    social_links: Mapped[list[SocialLink]] = mapped_column(
        ARRAY(SocialLinkType), default=list, nullable=False
    )
