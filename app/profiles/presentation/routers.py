from uuid import UUID

from fastapi import Depends
from fastapi.routing import APIRouter

from app.identity.application.use_cases import AuthenticateUserByTokenUseCase
from app.identity.presentation.dependencies import get_current_user_token
from app.identity.presentation.router import auth_user_dependency
from app.profiles.application.dto import ProfileResponse, UpdateProfileRequest
from app.profiles.application.use_cases import (
    GetUserProfileByUserIdUseCase,
    UpdateUserProfileUseCase,
)
from app.profiles.infrastructure.repositories import ProfilesRepository
from app.shared.infrastructure.database import UnitOfWork, get_uow

profiles = APIRouter(prefix="/profiles", tags=["profiles"])


async def get_profile_by_user_id(uow: UnitOfWork = Depends(get_uow)):
    return GetUserProfileByUserIdUseCase(ProfilesRepository(uow.session))


async def update_profile_dependency(uow: UnitOfWork = Depends(get_uow)):
    return UpdateUserProfileUseCase(ProfilesRepository(uow.session))


@profiles.get("/{user_id}", response_model=ProfileResponse)
async def get_profile(
    user_id: UUID,
    get_profile: GetUserProfileByUserIdUseCase = Depends(get_profile_by_user_id),
):
    response = await get_profile.execute(user_id)

    return response


@profiles.get("/me", response_model=ProfileResponse)
async def get_me(
    user_token: str = Depends(get_current_user_token),
    auth_use_case: AuthenticateUserByTokenUseCase = Depends(auth_user_dependency),
    get_profile: GetUserProfileByUserIdUseCase = Depends(get_profile_by_user_id),
):
    user_id = await auth_use_case.execute(user_token)
    response = await get_profile.execute(user_id)

    return response


@profiles.put("/me", response_model=ProfileResponse)
async def update_profile(
    request: UpdateProfileRequest,
    user_token: str = Depends(get_current_user_token),
    auth_use_case: AuthenticateUserByTokenUseCase = Depends(auth_user_dependency),
    update_profile_use_case: UpdateUserProfileUseCase = Depends(
        update_profile_dependency
    ),
):
    user_id = await auth_use_case.execute(user_token)
    response = await update_profile_use_case.execute(user_id, request)
    return response
