from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ProfileResponse(BaseModel):
    user_id: UUID
    display_name: str
    bio: str | None = None
    avatar_url: str | None = None
    social_links: list[dict[str, str]] = Field(default_factory=list[Any])


class UpdateProfileRequest(BaseModel):
    display_name: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
