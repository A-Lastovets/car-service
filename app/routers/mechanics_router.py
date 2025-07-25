from fastapi import APIRouter, Depends, HTTPException
from app.models.mechanic import Mechanic
from app.schemas.mechanic_schema import MechanicCreateSchema, MechanicResponseSchema, MechanicLoginSchema
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.database import get_db
from typing import List
from app.utils.auth import admin_required, authenticate_mechanic
from app.utils.tokens import create_access_token
from app.utils.password import get_password_hash
from passlib.context import CryptContext

router = APIRouter(prefix="/mechanics", tags=["Mechanics"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/", response_model=MechanicResponseSchema)
async def create_mechanic(mechanic: MechanicCreateSchema, db: AsyncSession = Depends(get_db), current_user=Depends(admin_required)):
    
    # Check if mechanic with this email already exists
    from sqlalchemy.future import select
    result = await db.execute(select(Mechanic).where(Mechanic.email == mechanic.email.lower()))
    existing_mechanic = result.scalar_one_or_none()
    if existing_mechanic:
        raise HTTPException(status_code=400, detail="Механік з такою поштою вже існує")
    
    # Hash password
    hashed_password = get_password_hash(mechanic.password)
    mechanic_data = mechanic.model_dump()
    mechanic_data["hashed_password"] = hashed_password
    del mechanic_data["password"]
    
    new_mechanic = Mechanic(**mechanic_data)
    db.add(new_mechanic)
    await db.commit()
    await db.refresh(new_mechanic)
    return new_mechanic

@router.post("/login")
async def mechanic_login(login_data: MechanicLoginSchema, db: AsyncSession = Depends(get_db)):
    """Login for mechanics using email/password from mechanics table"""
    mechanic = await authenticate_mechanic(db, login_data.email, login_data.password)
    
    if not mechanic:
        raise HTTPException(status_code=401, detail="Невірна пошта або пароль")
    
    # Create token for mechanic
    token = create_access_token(mechanic)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/", response_model=List[MechanicResponseSchema])
async def get_mechanics(db: AsyncSession = Depends(get_db)):
    from sqlalchemy.future import select
    result = await db.execute(select(Mechanic))
    return result.scalars().all()

@router.put("/{mechanic_id}", response_model=MechanicResponseSchema)
async def update_mechanic(mechanic_id: int, mechanic: MechanicCreateSchema, db: AsyncSession = Depends(get_db), current_user=Depends(admin_required)):
    
    from sqlalchemy.future import select
    result = await db.execute(select(Mechanic).where(Mechanic.id == mechanic_id))
    db_mechanic = result.scalar_one_or_none()
    if not db_mechanic:
        raise HTTPException(status_code=404, detail="Механіка не знайдено")
    
    # Hash password if it's being changed
    mechanic_data = mechanic.model_dump()
    if mechanic_data.get("password"):
        mechanic_data["hashed_password"] = get_password_hash(mechanic_data["password"])
        del mechanic_data["password"]
    
    for key, value in mechanic_data.items():
        setattr(db_mechanic, key, value)
    
    await db.commit()
    await db.refresh(db_mechanic)
    return db_mechanic

@router.delete("/{mechanic_id}")
async def delete_mechanic(mechanic_id: int, db: AsyncSession = Depends(get_db), current_user=Depends(admin_required)):
    
    from sqlalchemy.future import select
    result = await db.execute(select(Mechanic).where(Mechanic.id == mechanic_id))
    db_mechanic = result.scalar_one_or_none()
    if not db_mechanic:
        raise HTTPException(status_code=404, detail="Механіка не знайдено")
    
    await db.delete(db_mechanic)
    await db.commit()
    return {"detail": "Механіка видалено"}
