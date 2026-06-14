from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.identity.application.dto import (
    LoginRequest,
    RegisterUserRequest,
    TokenResponse,
    UserResponse,
)
from app.identity.application.handlers import (
    LoginHandler,
    LogoutHandler,
    RegisterUserhandler,
    VerifyUserByTokenHandler,
)
from app.identity.domain.entities import User
from app.identity.infrastructure.repository import AccessTokenRepository, UserRepository
from app.identity.infrastructure.security import PasswordHasher, TokenService
from app.shared.infrastructure.database import get_uow

auth = APIRouter(prefix="/auth")

bearer_scheme = HTTPBearer()


async def register_handler(uow=Depends(get_uow)):
    return RegisterUserhandler(UserRepository(uow.session), PasswordHasher())


async def login_handler(uow=Depends(get_uow)):
    return LoginHandler(
        UserRepository(uow.session),
        AccessTokenRepository(uow.session),
        PasswordHasher(),
        TokenService(),
    )


async def logout_handler(uow=Depends(get_uow)):
    return LogoutHandler(AccessTokenRepository(uow.session))


async def verify_user_handler(uow=Depends(get_uow)):
    return VerifyUserByTokenHandler(
        UserRepository(uow.session),
        AccessTokenRepository(uow.session),
        TokenService(),
    )


@auth.post("/register", response_model=UserResponse, status_code=201)
async def register(request: RegisterUserRequest, handler=Depends(register_handler)):
    return await handler.handle(request)


@auth.post("/login", response_model=TokenResponse, status_code=200)
async def login(request: LoginRequest, handler=Depends(login_handler)):
    return await handler.handle(request)


@auth.post("/logout", status_code=204)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    verify_handler=Depends(verify_user_handler),
    logout_handler=Depends(logout_handler),
):
    user = await verify_handler.handle(credentials.credentials)
    await logout_handler.handle(user.id)


@auth.get("/me", response_model=UserResponse, status_code=200)
async def get_me(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    verify_handler=Depends(verify_user_handler),
):
    user: User = await verify_handler.handle(credentials.credentials)
    return UserResponse(
        id=user.id,
        username=str(user.username),
        email=str(user.email),
        role=str(user.role),
    )
