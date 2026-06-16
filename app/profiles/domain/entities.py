from dataclasses import dataclass, field
from uuid import UUID

from app.profiles.domain.value_objects import Bio, DisplayedName, SocialLink
from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.value_objects import Url


@dataclass(slots=True)
class UserProfile(BaseEntity):
    user_id: UUID
    displayed_name: DisplayedName
    avatar_url: Url | None = None
    bio: Bio | None = None
    social_links: list[SocialLink] = field(default_factory=list[SocialLink])

    def set_displayed_name(self, new_displayed_name: DisplayedName):
        self.displayed_name = new_displayed_name
        self._touch()

    def set_avatar_url(self, new_avatar_url: Url):
        self.avatar_url = new_avatar_url
        self._touch()

    def set_bio(self, new_bio: Bio):
        self.bio = new_bio
        self._touch()

    def add_social_link(self, social_link: SocialLink):
        if social_link in self.social_links:
            return

        self.social_links.append(social_link)
        self._touch()
