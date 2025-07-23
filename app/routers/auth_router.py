from fastapi import APIRouter, HTTPException, Depends
from app.schemas.user_schema import UserCreateSchema, UserRegisterSchema, UserResponseSchema
from app.models.user import User
from app.utils.auth import authenticate_user
from app.utils.tokens import create_access_token
from app.utils.password import get_password_hash
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.database import get_db
from app.utils.password import validate_password, update_password

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponseSchema)
async def register(user: UserRegisterSchema, db: Session = Depends(get_db)):
    """Register a new customer. Role is automatically set to 'customer'."""
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Користувач уже існує")
    hashed_password = get_password_hash(user.password)
    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        role="customer"  # Automatically set to customer
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
async def login(user: UserCreateSchema, db: AsyncSession = Depends(get_db)):
    db_user = await authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Невірний логін або пароль")
    token = create_access_token(db_user)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/change-password")
async def change_password(email: str, new_password: str, db: AsyncSession = Depends(get_db)):
    validate_password(new_password)
    updated_user = await update_password(db, email, new_password)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Password updated successfully"}

