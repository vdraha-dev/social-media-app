from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.profiles.domain.entities import UserProfile
from app.profiles.domain.repositories import IProfileRepository
from app.profiles.infrastructure.models import UserProfileModel


class ProfilesRepository(IProfileRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, profile: UserProfile):
        db_profile = await self.get_by_user_id(profile.user_id)
        if db_profile:
            db_profile.set_displayed_name(profile.displayed_name)
            db_profile.set_avatar_url(profile.avatar_url)
            db_profile.set_bio(profile.bio)
            db_profile.add_social_links(profile.social_links)
        else:
            self.session.add(self._to_model(profile))

        await self.session.flush()

    async def get_by_user_id(self, user_id: UUID) -> UserProfile | None:
        stmt = select(UserProfileModel).where(UserProfileModel.user_id == user_id)
        result = await self.session.execute(stmt)
        profile_model = result.scalar_one_or_none()
        return self._to_entity(profile_model) if profile_model else None

    def _to_model(self, profile: UserProfile) -> UserProfileModel:
        return UserProfileModel(
            id=profile.id,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
            user_id=profile.user_id,
            displayed_name=profile.displayed_name,
            avatar_url=profile.avatar_url,
            bio=profile.bio,
            social_links=profile.social_links,
        )

    def _to_entity(self, model: UserProfileModel) -> UserProfile:
        return UserProfile(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            user_id=model.user_id,
            displayed_name=model.displayed_name,
            avatar_url=model.avatar_url,
            bio=model.bio,
            social_links=model.social_links,
        )
