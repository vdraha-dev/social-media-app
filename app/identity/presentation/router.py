from fastapi import APIRouter, Depends

from app.identity.presentation.dto import (
    LoginRequest,
    RegisterUserRequest,
    TokenResponse,
    UserResponse,
)
from app.identity.application.use_cases import (
    AuthenticateUserByTokenUseCase,
    LoginUseCase,
    LogoutUseCase,
    RegisterUserUseCase,
)
from app.identity.domain.entities import User
from app.identity.domain.value_objects import HashedPassword, Role, RoleEnum, UserName
from app.identity.infrastructure.repository import AccessTokenRepository, UserRepository
from app.identity.infrastructure.security import PasswordHasher, TokenService
from app.identity.presentation.dependencies import get_current_user_token
from app.shared.domain.value_objects import Email
from app.shared.infrastructure.database import UnitOfWork, get_uow

auth = APIRouter(prefix="/auth", tags=["authentication"])


async def register_dependency(
    uow: UnitOfWork = Depends(get_uow),
) -> RegisterUserUseCase:
    return RegisterUserUseCase(UserRepository(uow.session), PasswordHasher())


async def login_dependency(uow: UnitOfWork = Depends(get_uow)) -> LoginUseCase:
    return LoginUseCase(
        UserRepository(uow.session),
        AccessTokenRepository(uow.session),
        PasswordHasher(),
        TokenService(),
    )


async def logout_dependency(uow: UnitOfWork = Depends(get_uow)) -> LogoutUseCase:
    return LogoutUseCase(AccessTokenRepository(uow.session))


async def auth_user_dependency(
    uow: UnitOfWork = Depends(get_uow),
) -> AuthenticateUserByTokenUseCase:
    return AuthenticateUserByTokenUseCase(
        UserRepository(uow.session),
        AccessTokenRepository(uow.session),
        TokenService(),
    )


@auth.post("/register", response_model=UserResponse, status_code=201)
async def register(
    request: RegisterUserRequest,
    use_case: RegisterUserUseCase = Depends(register_dependency),
):
    user = User(
        username=UserName(request.username),
        email=Email(request.email),
        password=HashedPassword(value="0"),
        role=Role(RoleEnum.User),
    )
    await use_case.execute(user, request.password)

    return UserResponse(
        id=user.id,
        username=str(user.username),
        email=str(user.email),
        role=str(user.role),
    )


@auth.post("/login", response_model=TokenResponse, status_code=200)
async def login(
    request: LoginRequest, use_case: LoginUseCase = Depends(login_dependency)
):
    token = await use_case.execute(Email(request.email), request.password)

    return TokenResponse(
        access_token=token,
        token_type="Bearer",
    )


@auth.post("/logout", status_code=204)
async def logout(
    current_user_token: str = Depends(get_current_user_token),
    auth_use_case: AuthenticateUserByTokenUseCase = Depends(auth_user_dependency),
    logout_use_case: LogoutUseCase = Depends(logout_dependency),
):
    user = await auth_use_case.execute(current_user_token)
    await logout_use_case.execute(user.id)


@auth.get("/me", response_model=UserResponse, status_code=200)
async def get_me(
    current_user_token: str = Depends(get_current_user_token),
    auth_use_case: AuthenticateUserByTokenUseCase = Depends(auth_user_dependency),
):
    user = await auth_use_case.execute(current_user_token)
    return UserResponse(
        id=user.id,
        username=str(user.username),
        email=str(user.email),
        role=str(user.role),
    )
