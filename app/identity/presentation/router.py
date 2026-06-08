from fastapi import APIRouter

from app.identity.application.dto import (
    LoginRequest,
    RegisterUserRequest,
    TokenResponse,
    UserResponse,
)

auth = APIRouter(prefix="auth")


@auth.post("/register", response_model=UserResponse, status_code=201)
async def register(request: RegisterUserRequest): ...


@auth.post("/login", response_model=TokenResponse, status_code=200)
async def login(request: LoginRequest): ...
