from uuid import UUID

from app.profiles.domain.entities import UserProfile
from app.profiles.domain.exceptions import UserProfileNotFound
from app.profiles.domain.repositories import IProfileRepository


class GetUserProfileByUserIdUseCase:
    def __init__(self, profile_repo: IProfileRepository):
        self.profile_repo = profile_repo

    async def execute(self, user_id: UUID) -> UserProfile:
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise UserProfileNotFound("User profile not found for user")

        return profile
