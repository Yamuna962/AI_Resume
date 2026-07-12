"""
Authentication dependency helpers.
"""
import uuid
from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.config import settings
from app.database.session import AsyncSessionLocal
from app.models.user import User
from app.repositories.user_repository import user_repo

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# Same scheme but auto_error=False so missing tokens return None instead of 401.
# Used only by get_optional_user.
_oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await user_repo.get_by_id(db, id=uuid.UUID(user_id))
    if user is None:
        raise credentials_exception
    return user


async def get_optional_user(
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(_oauth2_scheme_optional),
) -> Optional[User]:
    """Return the authenticated user, or None when no token is provided.

    Uses a separate OAuth2 scheme with auto_error=False so FastAPI does NOT
    raise 401 during dependency injection when the Authorization header is
    absent. The previous implementation used the strict oauth2_scheme, which
    meant the 401 was thrown before the function body could catch it.
    """
    if not token:
        return None
    try:
        return await get_current_user(db, token)
    except HTTPException:
        return None
