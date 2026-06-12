from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator


class RegisterUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_validator(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v

    @field_validator("username")
    @classmethod
    def username_validator(cls, v):
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters long")
        return v


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    role: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
