from uuid import UUID

from fastapi import Depends
from fastapi.routing import APIRouter

from app.identity.application.use_cases import AuthenticateUserByTokenUseCase
from app.identity.infrastructure.repository import AccessTokenRepository
from app.identity.infrastructure.security import TokenService
from app.identity.presentation.dependencies import get_current_user_token
from app.profiles.application.dto import ProfileResponse, UpdateProfileRequest
from app.profiles.application.use_cases import (
    GetUserProfileByUserIdUseCase,
    UpdateUserProfileUseCase,
)
from app.profiles.infrastructure.repositories import ProfilesRepository
from app.shared.infrastructure.database import UnitOfWork, get_uow

profiles = APIRouter(prefix="/profiles", tags=["profiles"])


@profiles.get("/{user_id}", response_model=ProfileResponse)
async def get_profile(user_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    response = await GetUserProfileByUserIdUseCase(
        ProfilesRepository(uow.session)
    ).execute(user_id)

    return response


@profiles.get("/me", response_model=ProfileResponse)
async def get_me(
    user_token: str = Depends(get_current_user_token),
    uow: UnitOfWork = Depends(get_uow),
):
    user_id = await AuthenticateUserByTokenUseCase(
        AccessTokenRepository(uow.session),
        TokenService(),
    ).execute(user_token)
    response = await GetUserProfileByUserIdUseCase(
        ProfilesRepository(uow.session)
    ).execute(user_id)

    return response


@profiles.put("/me", response_model=ProfileResponse)
async def update_profile(
    request: UpdateProfileRequest,
    user_token: str = Depends(get_current_user_token),
    uow: UnitOfWork = Depends(get_uow),
):
    user_id = await AuthenticateUserByTokenUseCase(
        AccessTokenRepository(uow.session),
        TokenService(),
    ).execute(user_token)
    response = await UpdateUserProfileUseCase(ProfilesRepository(uow.session)).execute(
        user_id, request
    )
    return response
