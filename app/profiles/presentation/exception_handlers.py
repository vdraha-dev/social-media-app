from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.profiles.domain.exceptions import UserProfileNotFound


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(UserProfileNotFound)
    async def user_profile_not_found_error(request: Request, err: UserProfileNotFound):  # pyright: ignore
        return JSONResponse(content=str(err), status_code=404)
