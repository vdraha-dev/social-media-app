from uuid import UUID

from fastapi import Depends
from fastapi.routing import APIRouter

from app.identity.application.use_cases import AuthenticateUserByTokenUseCase
from app.identity.presentation.dependencies import get_current_user_token
from app.identity.presentation.router import (
    AccessTokenRepository,
    TokenService,
    UserRepository,
)
from app.profiles.application.use_cases import (
    GetUserProfileByUserIdUseCase,
    UpdateUserProfileUseCase,
)
from app.profiles.domain.value_objects import Bio, DisplayedName
from app.profiles.infrastructure.repositories import ProfilesRepository
from app.profiles.presentation.dto import ProfileResponse, UpdateProfileRequest
from app.shared.domain.value_objects import Url
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


async def update_profile_dependency(uow: UnitOfWork = Depends(get_uow)):
    return UpdateUserProfileUseCase(ProfilesRepository(uow.session))


@profiles.get("/{user_id}", response_model=ProfileResponse)
async def get_profile(
    user_id: UUID,
    get_profile: GetUserProfileByUserIdUseCase = Depends(get_profile_by_user_id),
):
    profile = await get_profile.execute(user_id)

    return ProfileResponse(
        user_id=profile.user_id,
        display_name=str(profile.displayed_name),
        bio=str(profile.bio) if profile.bio else None,
        avatar_url=str(profile.avatar_url) if profile.avatar_url else None,
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
        bio=str(profile.bio) if profile.bio else None,
        avatar_url=str(profile.avatar_url) if profile.avatar_url else None,
        social_links=[link.to_dict() for link in profile.social_links],
    )


@profiles.put("/me", response_model=ProfileResponse)
async def update_profile(
    request: UpdateProfileRequest,
    user_token: str = Depends(get_current_user_token),
    auth_use_case: AuthenticateUserByTokenUseCase = Depends(auth_user_dependency),
    get_profile_use_case: GetUserProfileByUserIdUseCase = Depends(
        get_profile_by_user_id
    ),
    update_profile_use_case: UpdateUserProfileUseCase = Depends(
        update_profile_dependency
    ),
):
    user = await auth_use_case.execute(user_token)
    profile = await get_profile_use_case.execute(user.id)

    updated_at = profile.updated_at

    profile.set_displayed_name(
        DisplayedName(request.display_name)
        if request.display_name
        else profile.displayed_name
    )
    profile.set_avatar_url(
        Url(request.avatar_url) if request.avatar_url else profile.avatar_url
    )
    profile.set_bio(Bio(request.bio) if request.bio else profile.bio)

    if updated_at != profile.updated_at:
        await update_profile_use_case.execute(profile)

    return ProfileResponse(
        user_id=profile.user_id,
        display_name=str(profile.displayed_name),
        bio=str(profile.bio) if profile.bio else None,
        avatar_url=str(profile.avatar_url) if profile.avatar_url else None,
        social_links=[link.to_dict() for link in profile.social_links],
    )
