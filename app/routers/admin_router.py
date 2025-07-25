from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.database import get_db
from app.models.user import User
from app.models.mechanic import Mechanic
from app.models.document import Document
from app.models.appointment import Appointment
from app.utils.auth import admin_required
from typing import List
from app.schemas.user_schema import UserCreateSchema

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/users", response_model=List[dict])
async def get_all_users(db: AsyncSession = Depends(get_db), current_user=Depends(admin_required)):
    from sqlalchemy.future import select
    result = await db.execute(select(User))
    users = result.scalars().all()
    return [
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
        for user in users
    ]

@router.get("/mechanics", response_model=List[dict])
async def get_all_mechanics(db: AsyncSession = Depends(get_db), current_user=Depends(admin_required)):
    from sqlalchemy.future import select
    result = await db.execute(select(Mechanic))
    mechanics = result.scalars().all()
    return [
        {
            "id": mechanic.id,
            "full_name": mechanic.full_name,
            "email": mechanic.email,
            "phone": mechanic.phone,
            "specialization": mechanic.specialization,
            "is_active": mechanic.is_active,
            "created_at": mechanic.created_at,
            "updated_at": mechanic.updated_at
        }
        for mechanic in mechanics
    ]

@router.get("/documents", response_model=List[dict])
async def get_all_documents(db: AsyncSession = Depends(get_db), current_user=Depends(admin_required)):
    from sqlalchemy.future import select
    result = await db.execute(select(Document))
    documents = result.scalars().all()
    return [
        {
            "id": document.id,
            "mechanic_id": document.mechanic_id,
            "type": document.type,
            "file_path": document.file_path
        }
        for document in documents
    ]

@router.get("/appointments", response_model=List[dict])
async def get_all_appointments(db: AsyncSession = Depends(get_db), current_user=Depends(admin_required)):
    from sqlalchemy.future import select
    result = await db.execute(select(Appointment))
    appointments = result.scalars().all()
    return [
        {
            "id": appointment.id,
            "user_id": appointment.user_id,
            "car_id": appointment.car_id,
            "service_id": appointment.service_id,
            "mechanic_id": appointment.mechanic_id,
            "appointment_date": appointment.appointment_date,
            "status": appointment.status
        }
        for appointment in appointments
    ]

@router.patch("/users/{user_id}/change_role")
async def change_user_role(user_id: int, user_update: UserCreateSchema, db: AsyncSession = Depends(get_db), current_user=Depends(admin_required)):
    
    from sqlalchemy.future import select
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    
    # Update all user fields
    for key, value in user_update.model_dump().items():
        if key == "password":
            # Hash password if it's being changed
            from app.utils.password import get_password_hash
            setattr(db_user, "hashed_password", get_password_hash(value))
        elif key == "name":
            # Map 'name' to 'full_name'
            setattr(db_user, "full_name", value)
        elif key == "phone":
            # Skip phone if not provided in schema
            continue
        else:
            setattr(db_user, key, value)
    
    await db.commit()
    await db.refresh(db_user)
    return {
        "detail": "Роль користувача успішно змінена", 
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "full_name": db_user.full_name,
            "phone": db_user.phone,
            "role": db_user.role,
            "is_active": db_user.is_active,
            "created_at": db_user.created_at,
            "updated_at": db_user.updated_at
        }
    }
