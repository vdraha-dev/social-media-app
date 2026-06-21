from uuid import UUID

from app.profiles.application.dto import ProfileResponse, UpdateProfileRequest
from app.profiles.domain.exceptions import UserProfileNotFound
from app.profiles.domain.repositories import IProfileRepository
from app.profiles.domain.value_objects import Bio, DisplayedName
from app.shared.domain.value_objects import Url


class GetUserProfileByUserIdUseCase:
    def __init__(self, profile_repo: IProfileRepository):
        self.profile_repo = profile_repo

    async def execute(self, user_id: UUID) -> ProfileResponse:
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise UserProfileNotFound("User profile not found for user")

        return ProfileResponse(
            user_id=profile.user_id,
            display_name=str(profile.displayed_name),
            bio=str(profile.bio) if profile.bio else None,
            avatar_url=str(profile.avatar_url) if profile.avatar_url else None,
            social_links=[link.to_dict() for link in profile.social_links],
        )


class UpdateUserProfileUseCase:
    def __init__(self, profile_repo: IProfileRepository):
        self.profile_repo = profile_repo

    async def execute(self, user_id: UUID, user_profile: UpdateProfileRequest):
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise UserProfileNotFound("User profile not found for user")

        updated_at = profile.updated_at

        if user_profile.display_name:
            profile.set_displayed_name(DisplayedName(user_profile.display_name))

        if user_profile.bio:
            profile.set_bio(Bio(user_profile.bio))

        if user_profile.avatar_url:
            profile.set_avatar_url(Url(user_profile.avatar_url))

        if updated_at != profile.updated_at:
            await self.profile_repo.save(profile)

        return ProfileResponse(
            user_id=profile.user_id,
            display_name=str(profile.displayed_name),
            bio=str(profile.bio) if profile.bio else None,
            avatar_url=str(profile.avatar_url) if profile.avatar_url else None,
            social_links=[link.to_dict() for link in profile.social_links],
        )
