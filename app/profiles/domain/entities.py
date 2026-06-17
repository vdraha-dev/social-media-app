from collections.abc import Iterable
from datetime import datetime
from uuid import UUID

from app.profiles.domain.value_objects import Bio, DisplayedName, SocialLink
from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects import Url


class UserProfile(BaseEntity):
    __slots__ = (
        "_user_id",
        "_displayed_name",
        "_avatar_url",
        "_bio",
        "_social_links",
    )

    def __init__(
        self,
        user_id: UUID,
        displayed_name: DisplayedName,
        avatar_url: Url | None = None,
        bio: Bio | None = None,
        social_links: list[SocialLink] | None = None,
        id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        super().__init__(id, created_at, updated_at)
        self._user_id = user_id
        self._displayed_name = displayed_name
        self._avatar_url = avatar_url
        self._bio = bio
        self._social_links = social_links if social_links else list[SocialLink]()

    @property
    def user_id(self) -> UUID:
        return self._user_id

    @property
    def displayed_name(self) -> DisplayedName:
        return self._displayed_name

    @property
    def avatar_url(self) -> Url | None:
        return self._avatar_url

    @property
    def bio(self) -> Bio | None:
        return self._bio

    @property
    def social_links(self) -> tuple[SocialLink, ...]:
        return tuple(self._social_links)

    def set_displayed_name(self, new_displayed_name: DisplayedName):
        if new_displayed_name == self._displayed_name:
            return

        self._displayed_name = new_displayed_name
        self._touch()

    def set_avatar_url(self, new_avatar_url: Url | None):
        if new_avatar_url == self._avatar_url:
            return

        self._avatar_url = new_avatar_url
        self._touch()

    def set_bio(self, new_bio: Bio | None):
        if new_bio == self._bio:
            return

        self.social_links.append(social_link)
        self._touch()
