from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user_schema import UserResponseSchema
from app.dependencies.database import get_db
from app.utils.auth import role_required_with_cache

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponseSchema)
async def get_profile(current_user=Depends(role_required_with_cache(["customer", "mechanic", "admin"]))):
    return current_user
