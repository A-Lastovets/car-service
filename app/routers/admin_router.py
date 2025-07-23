from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.models.user import User
from app.models.mechanic import Mechanic
from app.models.document import Document
from app.models.appointment import Appointment
from app.utils.auth import get_current_user
from typing import List
from app.schemas.user_schema import UserCreateSchema

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/users", response_model=List[dict])
async def get_all_users(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Тільки адміністратор")
    users = db.query(User).all()
    return [u.__dict__ for u in users]

@router.get("/mechanics", response_model=List[dict])
async def get_all_mechanics(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Тільки адміністратор")
    mechanics = db.query(Mechanic).all()
    return [m.__dict__ for m in mechanics]

@router.get("/documents", response_model=List[dict])
async def get_all_documents(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Тільки адміністратор")
    documents = db.query(Document).all()
    return [d.__dict__ for d in documents]

@router.get("/appointments", response_model=List[dict])
async def get_all_appointments(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Тільки адміністратор")
    appointments = db.query(Appointment).all()
    return [a.__dict__ for a in appointments]

@router.patch("/users/{user_id}/change_role")
async def change_user_role(user_id: int, user_update: UserCreateSchema, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Тільки адміністратор може змінювати ролі користувачів")
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    
    # Update all user fields
    for key, value in user_update.model_dump().items():
        if key == "password":
            # Hash password if it's being changed
            from app.utils.password import get_password_hash
            setattr(db_user, "password", get_password_hash(value))
        else:
            setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return {"detail": "Роль користувача успішно змінена", "user": db_user.__dict__}
