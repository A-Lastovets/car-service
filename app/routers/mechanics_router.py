from fastapi import APIRouter, Depends, HTTPException
from app.models.mechanic import Mechanic
from app.schemas.mechanic_schema import MechanicCreateSchema, MechanicResponseSchema, MechanicLoginSchema
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from typing import List
from app.utils.auth import get_current_user, authenticate_mechanic
from app.utils.tokens import create_access_token
from app.utils.password import get_password_hash
from passlib.context import CryptContext

router = APIRouter(prefix="/mechanics", tags=["Mechanics"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/", response_model=MechanicResponseSchema)
async def create_mechanic(mechanic: MechanicCreateSchema, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Тільки адміністратор може створювати механіків")
    
    # Check if mechanic with this login already exists
    existing_mechanic = db.query(Mechanic).filter(Mechanic.login == mechanic.login).first()
    if existing_mechanic:
        raise HTTPException(status_code=400, detail="Механік з таким логіном вже існує")
    
    # Hash password
    hashed_password = get_password_hash(mechanic.password)
    mechanic_data = mechanic.model_dump()
    mechanic_data["password"] = hashed_password
    
    new_mechanic = Mechanic(**mechanic_data)
    db.add(new_mechanic)
    db.commit()
    db.refresh(new_mechanic)
    return new_mechanic

@router.post("/login")
async def mechanic_login(login_data: MechanicLoginSchema, db: Session = Depends(get_db)):
    """Login for mechanics using login/password from mechanics table"""
    mechanic = await authenticate_mechanic(db, login_data.login, login_data.password)
    
    if not mechanic:
        raise HTTPException(status_code=401, detail="Невірний логін або пароль")
    
    # Create token for mechanic
    token = create_access_token(mechanic)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/", response_model=List[MechanicResponseSchema])
async def get_mechanics(db: Session = Depends(get_db)):
    return db.query(Mechanic).all()

@router.put("/{mechanic_id}", response_model=MechanicResponseSchema)
async def update_mechanic(mechanic_id: int, mechanic: MechanicCreateSchema, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Тільки адміністратор може змінювати механіків")
    db_mechanic = db.query(Mechanic).filter(Mechanic.id == mechanic_id).first()
    if not db_mechanic:
        raise HTTPException(status_code=404, detail="Механіка не знайдено")
    
    # Hash password if it's being changed
    mechanic_data = mechanic.model_dump()
    if mechanic_data.get("password"):
        mechanic_data["password"] = get_password_hash(mechanic_data["password"])
    
    for key, value in mechanic_data.items():
        setattr(db_mechanic, key, value)
    
    db.commit()
    db.refresh(db_mechanic)
    return db_mechanic

@router.delete("/{mechanic_id}")
async def delete_mechanic(mechanic_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Тільки адміністратор може видаляти механіків")
    db_mechanic = db.query(Mechanic).filter(Mechanic.id == mechanic_id).first()
    if not db_mechanic:
        raise HTTPException(status_code=404, detail="Механіка не знайдено")
    db.delete(db_mechanic)
    db.commit()
    return {"detail": "Механіка видалено"}
