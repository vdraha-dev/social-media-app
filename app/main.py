from fastapi import FastAPI

from app.identity.presentation.exception_handlers import (
    register_exception_handlers as identity_handlers,
)
from app.identity.presentation.router import auth
from app.shared.presentation.exception_handlers import (
    register_exception_handlers as shared_handlers,
)

app = FastAPI(docs_url="/docs", title="Social Media App")
shared_handlers(app)

app.include_router(auth)
identity_handlers(app)
