from http.cookies import SimpleCookie
from typing import List

from fastapi import Depends, HTTPException, Request, WebSocket, status
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from fastapi.security import OAuth2PasswordBearer

from app.dependencies.cache import redis_client
from app.dependencies.database import get_db
from app.models.user import User
from app.models.mechanic import Mechanic
from app.utils.tokens import decode_jwt_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/sign-in-swagger")


# Get user by email
async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email.lower()))
    return result.scalar_one_or_none()


# Get mechanic by email
async def get_mechanic_by_email(db: AsyncSession, email: str) -> Mechanic | None:
    result = await db.execute(select(Mechanic).where(Mechanic.email == email.lower()))
    return result.scalar_one_or_none()


# Get user by token without blocking check
async def get_current_user_id(request: Request) -> int:
    """Get user_id from JWT token in cookie"""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token_data = decode_jwt_token(token)
    user_id = int(token_data["id"])
    return user_id


# User authentication
async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email.lower()))
    user = result.scalar_one_or_none()

    if not user or not pwd_context.verify(password, user.hashed_password):
        return None
    return user


# Mechanic authentication
async def authenticate_mechanic(db: AsyncSession, email: str, password: str) -> Mechanic | None:
    result = await db.execute(select(Mechanic).where(Mechanic.email == email.lower()))
    mechanic = result.scalar_one_or_none()

    if not mechanic or not pwd_context.verify(password, mechanic.hashed_password):
        return None
    return mechanic


async def get_user_from_token(token: str, db: AsyncSession):
    token_data = decode_jwt_token(token)
    user_type = token_data.get("type", "user")
    user_id = int(token_data["id"])
    role = token_data.get("role")
    if user_type == "user":
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    else:
        mechanic = await db.get(Mechanic, user_id)
        if not mechanic:
            raise HTTPException(status_code=404, detail="Mechanic not found")
        return mechanic

async def admin_required(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    redis = Depends(redis_client.get_redis),
):
    cache_key = f"admin_check:{token}"
    cached = await redis.get(cache_key)
    # Ignore cache for user object, always return full user
    user = await get_user_from_token(token, db)
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Admin role required",
        )
    await redis.set(cache_key, f"{user.id}:{user.role}", ex=300)
    return user

async def mechanic_required(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    redis = Depends(redis_client.get_redis),
):
    cache_key = f"mechanic_check:{token}"
    cached = await redis.get(cache_key)
    user = await get_user_from_token(token, db)
    if user.role not in ["mechanic", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Mechanic or Admin role required",
        )
    await redis.set(cache_key, f"{user.id}:{user.role}", ex=300)
    return user

async def customer_required(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    redis = Depends(redis_client.get_redis),
):
    cache_key = f"customer_check:{token}"
    cached = await redis.get(cache_key)
    user = await get_user_from_token(token, db)
    if user.role not in ["customer", "mechanic", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Customer, Mechanic or Admin role required",
        )
    await redis.set(cache_key, f"{user.id}:{user.role}", ex=300)
    return user

# Generic role checker with cache
def role_required_with_cache(roles: List[str]):
    async def dependency(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db),
        redis = Depends(redis_client.get_redis),
    ):
        cache_key = f"role_check:{'-'.join(roles)}:{token}"
        cached = await redis.get(cache_key)
        user = await get_user_from_token(token, db)
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Required roles: {roles}",
            )
        await redis.set(cache_key, f"{user.id}:{user.role}", ex=300)
        return user
    return dependency
