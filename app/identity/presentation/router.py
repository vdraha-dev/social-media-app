from fastapi import APIRouter

from app.identity.application.dto import RegisterUserRequest, UserResponse

auth = APIRouter(prefix="auth")


@auth.post("/register", response_model=UserResponse, status_code=201)
async def register(request: RegisterUserRequest): ...
