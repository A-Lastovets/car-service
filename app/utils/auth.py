from http.cookies import SimpleCookie

from fastapi import Depends, HTTPException, Request, WebSocket, status
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func

from app.dependencies.database import get_db
from app.models.user import User
from app.models.mechanic import Mechanic
from app.utils.tokens import decode_jwt_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Get user by email
async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email.lower()))
    return result.scalar_one_or_none()


# Get mechanic by login
async def get_mechanic_by_login(db: AsyncSession, login: str) -> Mechanic | None:
    result = await db.execute(select(Mechanic).where(Mechanic.login == login))
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
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not pwd_context.verify(password, user.password):
        return None
    return user


# Mechanic authentication
async def authenticate_mechanic(db: AsyncSession, login: str, password: str) -> Mechanic | None:
    result = await db.execute(select(Mechanic).where(Mechanic.login == login))
    mechanic = result.scalar_one_or_none()

    if not mechanic or not pwd_context.verify(password, mechanic.password):
        return None
    return mechanic


async def admin_required(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token_data = decode_jwt_token(token)
    admin_id = token_data.get("id")
    role = token_data.get("role")

    if role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Access denied: Admin role required",
        )

    return {"id": admin_id, "role": role}

async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User | Mechanic:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token_data = decode_jwt_token(token)
    user_type = token_data.get("type", "user")
    user_id = int(token_data["id"])

    if user_type == "user":
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    else:  # mechanic
        mechanic = await db.get(Mechanic, user_id)
        if not mechanic:
            raise HTTPException(status_code=404, detail="Mechanic not found")
        return mechanic
