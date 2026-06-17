from uuid import UUID

from fastapi import Depends
from fastapi.routing import APIRouter

from app.identity.application.handlers import AuthenticateUserByTokenUseCase
from app.identity.presentation.dependencies import get_current_user_token
from app.identity.presentation.router import (
    AccessTokenRepository,
    TokenService,
    UserRepository,
)
from app.profiles.application.dto import ProfileResponse
from app.profiles.application.use_cases import GetUserProfileByUserIdUseCase
from app.profiles.infrastructure.repositories import ProfilesRepository
from app.shared.infrastructure.database import UnitOfWork, get_uow

profiles = APIRouter(prefix="/profiles", tags=["profiles"])


async def auth_user_dependency(uow: UnitOfWork = Depends(get_uow)):
    return AuthenticateUserByTokenUseCase(
        UserRepository(uow.session),
        AccessTokenRepository(uow.session),
        TokenService(),
    )


async def get_profile_by_user_id(uow: UnitOfWork = Depends(get_uow)):
    return GetUserProfileByUserIdUseCase(ProfilesRepository(uow.session))


@profiles.get("/{user_id}", response_model=ProfileResponse)
async def get_profile(
    user_id: UUID,
    get_profile: GetUserProfileByUserIdUseCase = Depends(get_profile_by_user_id),
):
    profile = await get_profile.execute(user_id)

    return ProfileResponse(
        user_id=profile.user_id,
        display_name=str(profile.displayed_name),
        bio=str(profile.bio),
        social_links=[link.to_dict() for link in profile.social_links],
    )


@profiles.get("/me", response_model=ProfileResponse)
async def get_me(
    user_token: str = Depends(get_current_user_token),
    auth_use_case: AuthenticateUserByTokenUseCase = Depends(auth_user_dependency),
    get_profile: GetUserProfileByUserIdUseCase = Depends(get_profile_by_user_id),
):
    user = await auth_use_case.execute(user_token)
    profile = await get_profile.execute(user.id)

    return ProfileResponse(
        user_id=profile.user_id,
        display_name=str(profile.displayed_name),
        bio=str(profile.bio),
        social_links=[link.to_dict() for link in profile.social_links],
    )


@profiles.put("/me")
async def update_profile(): ...
