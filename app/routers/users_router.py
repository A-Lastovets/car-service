from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user_schema import UserResponseSchema
from app.dependencies.database import get_db
from app.utils.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponseSchema)
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user
