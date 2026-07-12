from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.repositories.user_repository import user_repo
from app.schemas.auth import Token, UserCreate, UserLogin, UserResponse


class AuthService:
    async def register(self, db: AsyncSession, user_in: UserCreate) -> UserResponse:
        user = await user_repo.get_by_email(db, email=user_in.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )
            
        hashed_password = get_password_hash(user_in.password)
        new_user = await user_repo.create(
            db,
            obj_in={
                "email": user_in.email,
                "hashed_password": hashed_password,
                "full_name": user_in.full_name,
            },
        )
        return UserResponse.model_validate(new_user)

    async def login(self, db: AsyncSession, login_in: UserLogin) -> Token:
        user = await user_repo.get_by_email(db, email=login_in.email)
        if not user or not verify_password(login_in.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=str(user.id), expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user),
        )


auth_service = AuthService()
