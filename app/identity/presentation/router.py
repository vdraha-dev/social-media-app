from fastapi import APIRouter, Depends

from app.identity.application.dto import (
    LoginRequest,
    RegisterUserRequest,
    TokenResponse,
    UserResponse,
)
from app.identity.domain.entities import User
from app.identity.presentation.dependencies import get_current_user

auth = APIRouter(prefix="auth")


@auth.post("/register", response_model=UserResponse, status_code=201)
async def register(request: RegisterUserRequest): ...


@auth.post("/login", response_model=TokenResponse, status_code=200)
async def login(request: LoginRequest): ...


@auth.post("/logout", status_code=204)
async def logout(current_use: User = Depends(get_current_user)): ...


@auth.get("/me", response_model=UserResponse, status_code=200)
async def get_me(current_user: User = Depends(get_current_user)):...