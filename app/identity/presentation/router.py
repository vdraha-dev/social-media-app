from fastapi import APIRouter, Depends

from app.identity.application.dto import (
    LoginRequest,
    RegisterUserRequest,
    TokenResponse,
    UserResponse,
)
from app.identity.application.use_cases import (
    AuthenticateUserByTokenUseCase,
    GetUserInfoByTokenUseCase,
    LoginUseCase,
    LogoutUseCase,
    RegisterUserUseCase,
)
from app.identity.infrastructure.repository import AccessTokenRepository, UserRepository
from app.identity.infrastructure.security import PasswordHasher, TokenService
from app.identity.presentation.dependencies import get_current_user_token
from app.shared.infrastructure.database import UnitOfWork, get_uow

auth = APIRouter(prefix="/auth", tags=["authentication"])


@auth.post("/register", response_model=UserResponse, status_code=201)
async def register(
    request: RegisterUserRequest,
    uow: UnitOfWork = Depends(get_uow),
):
    response = await RegisterUserUseCase(
        UserRepository(uow.session), PasswordHasher()
    ).execute(request)

    return response


@auth.post("/login", response_model=TokenResponse, status_code=200)
async def login(
    request: LoginRequest,
    uow: UnitOfWork = Depends(get_uow),
):
    response = await LoginUseCase(
        UserRepository(uow.session),
        AccessTokenRepository(uow.session),
        PasswordHasher(),
        TokenService(),
    ).execute(request)

    return response


@auth.post("/logout", status_code=204)
async def logout(
    current_user_token: str = Depends(get_current_user_token),
    uow: UnitOfWork = Depends(get_uow),
):
    user_id = await AuthenticateUserByTokenUseCase(
        AccessTokenRepository(uow.session),
        TokenService(),
    ).execute(current_user_token)

    await LogoutUseCase(AccessTokenRepository(uow.session)).execute(user_id)


@auth.get("/me", response_model=UserResponse, status_code=200)
async def get_me(
    current_user_token: str = Depends(get_current_user_token),
    uow: UnitOfWork = Depends(get_uow),
):
    user_id = await AuthenticateUserByTokenUseCase(
        AccessTokenRepository(uow.session),
        TokenService(),
    ).execute(current_user_token)

    response = await GetUserInfoByTokenUseCase(UserRepository(uow.session)).execute(
        user_id
    )
    return response
