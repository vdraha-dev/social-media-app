from uuid import UUID

from app.profiles.application.dto import ProfileResponse
from app.profiles.domain.exceptions import UserProfileNotFound
from app.profiles.domain.repositories import IProfileRepository


class GetUserProfileByUserIdUseCase:
    def __init__(self, profile_repo: IProfileRepository):
        self.profile_repo = profile_repo

    async def execute(self, user_id: UUID):
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise UserProfileNotFound("User profile not found for user")

        return ProfileResponse(
            user_id=profile.user_id,
            display_name=str(profile.displayed_name),
            bio=str(profile.bio),
            social_links=[link.to_dict() for link in profile.social_links],
        )
