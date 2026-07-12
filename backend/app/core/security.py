"""
Security utilities: JWT token creation/verification and bcrypt password hashing.
"""
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from loguru import logger

from app.core.config import settings


# ── Password Context ──────────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(plain_password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a stored bcrypt hash."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as exc:
        logger.error(f"Password verification error: {exc}")
        return False


# ── JWT Utilities ─────────────────────────────────────────────────────────────
def create_access_token(
    subject: str | Any,
    extra_claims: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a signed JWT access token.

    Args:
        subject: The token subject (usually the user's UUID string).
        extra_claims: Optional additional claims to embed in the token.
        expires_delta: Custom expiry override; defaults to settings.ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        Encoded JWT string.
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": now,
        "exp": expire,
        "type": "access",
    }

    if extra_claims:
        payload.update(extra_claims)

    encoded_jwt = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT access token.

    Args:
        token: The raw JWT string.

    Returns:
        The decoded payload as a dict.

    Raises:
        HTTPException 401 if the token is invalid or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        subject: str | None = payload.get("sub")
        token_type: str | None = payload.get("type")

        if subject is None:
            logger.warning("JWT decode: missing 'sub' claim.")
            raise credentials_exception

        if token_type != "access":
            logger.warning(f"JWT decode: unexpected token type '{token_type}'.")
            raise credentials_exception

        return payload

    except JWTError as exc:
        logger.warning(f"JWT decode error: {exc}")
        raise credentials_exception from exc


def extract_user_id_from_token(token: str) -> str:
    """
    Convenience function to extract just the user_id (sub) from a token.

    Returns:
        The user UUID string.

    Raises:
        HTTPException 401 on invalid token.
    """
    payload = decode_access_token(token)
    return payload["sub"]
