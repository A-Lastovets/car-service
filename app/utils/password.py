import re

from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.auth import get_user_by_email

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def update_password(db: AsyncSession, email: str, new_password: str):
    user = await get_user_by_email(db, email)
    if not user:
        return None

    validate_password_schema(new_password)
    user.password = pwd_context.hash(new_password)
    await db.commit()
    return user


def validate_password(password: str):
    """
    Checks if the password meets security requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one digit
    - At least one special character (!@#$%^&*()_+ etc.)
    """
    if len(password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters long.",
        )
    if not re.search(r"[A-Z]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one uppercase letter.",
        )
    if not re.search(r"\d", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one digit.",
        )
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one special character.",
        )
    return password


def validate_password_schema(password: str):
    """
    Версія `validate_password`, яка підходить для використання в Pydantic-схемах
    (викидає ValueError замість HTTPException).
    """
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    if not any(c.isupper() for c in password):
        raise ValueError("Password must contain at least one uppercase letter.")
    if not any(c.isdigit() for c in password):
        raise ValueError("Password must contain at least one digit.")
    if not any(c in '!@#$%^&*(),.?":{}|<>' for c in password):
        raise ValueError("Password must contain at least one special character.")
    return password
