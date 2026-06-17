from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.shared.domain.exceptions import (
    AlreadyExistsError,
    ConflictError,
    DomainError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(NotFoundError)
    async def not_found_error_handler(request: Request, exc: NotFoundError):  # pyright: ignore
        return JSONResponse(
            status_code=404, content={"detail": str(exc), "code": "NOT_FOUND"}
        )

    @app.exception_handler(AlreadyExistsError)
    async def already_exists_error_handler(request: Request, exc: AlreadyExistsError):  # pyright: ignore
        return JSONResponse(
            status_code=409, content={"detail": str(exc), "code": "ALREADY_EXISTS"}
        )

    @app.exception_handler(PermissionDeniedError)
    async def permission_denied_error_handler(  # pyright: ignore
        request: Request, exc: PermissionDeniedError
    ):
        return JSONResponse(
            status_code=403, content={"detail": str(exc), "code": "PERMISSION_DENIED"}
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):  # pyright: ignore
        return JSONResponse(
            status_code=422, content={"detail": str(exc), "code": "VALIDATION_ERROR"}
        )

    @app.exception_handler(ConflictError)
    async def conflict_error_handler(request: Request, exc: ConflictError):  # pyright: ignore
        return JSONResponse(
            status_code=409, content={"detail": str(exc), "code": "CONFLICT"}
        )

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError):  # pyright: ignore
        return JSONResponse(
            status_code=400, content={"detail": str(exc), "code": "DOMAIN_ERROR"}
        )
