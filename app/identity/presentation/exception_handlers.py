from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.identity.domain.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
    UserAlreadyExistsError,
)


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(TokenExpiredError)
    async def token_expired_error(request: Request, err: TokenExpiredError):
        return JSONResponse(content=str(err), status_code=403)

    @app.exception_handler(InvalidTokenError)
    async def invalid_token_error(request: Request, err: InvalidTokenError):
        return JSONResponse(content=str(err), status_code=403)

    @app.exception_handler(UserAlreadyExistsError)
    async def user_already_exist_error(request: Request, err: UserAlreadyExistsError):
        return JSONResponse(content=str(err), status_code=409)

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_error(request: Request, err: InvalidCredentialsError):
        return JSONResponse(content=str(err), status_code=401)
