from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.identity.domain.entities import User

bearer_scheme = HTTPBearer()


async def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> User:
    return credentials.credentials
