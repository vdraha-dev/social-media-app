from fastapi import FastAPI

from app.identity.presentation.router import auth

app = FastAPI(docs_url="/docs", title="Social Media App")

app.include_router(auth)
