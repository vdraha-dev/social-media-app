from fastapi import APIRouter, Depends

from app.identity.application.dto import (
    LoginRequest,
    RegisterUserRequest,
    TokenResponse,
    UserResponse,
)
from app.identity.application.handlers import LoginHandler, LogoutHandler, RegisterUserhandler
from app.identity.domain.entities import User
from app.identity.infrastructure.repository import AccessTokenRepository, UserRepository
from app.identity.infrastructure.security import PasswordHasher, TokenService
from app.identity.presentation.dependencies import get_current_user
from app.shared.infrastructure.database import get_session

auth = APIRouter(prefix="/auth")


async def register_handler(session=Depends(get_session)):
    return RegisterUserhandler(UserRepository(session), PasswordHasher(session))


async def login_handler(session=Depends(get_session)):
    return LoginHandler(
        UserRepository(session),
        AccessTokenRepository(session),
        PasswordHasher(session),
        TokenService(session),
    )
    

async def logout_handler(session=Depends(get_session)):
    return LogoutHandler(AccessTokenRepository(session))


@auth.post("/register", response_model=UserResponse, status_code=201)
async def register(request: RegisterUserRequest, handler=Depends(register_handler)):
    return await handler.handle(request)


@auth.post("/login", response_model=TokenResponse, status_code=200)
async def login(request: LoginRequest, handler=Depends(login_handler)):
    return await handler.handle(request)


@auth.post("/logout", status_code=204)
async def logout(current_user: User = Depends(get_current_user), handler=Depends(logout_handler)):
    return await handler.handle(current_user.id)


@auth.get("/me", response_model=UserResponse, status_code=200)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
    )
