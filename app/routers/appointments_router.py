from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.appointment_schema import AppointmentCreateSchema, AppointmentResponseSchema
from app.models.appointment import Appointment
from app.dependencies.database import get_db
from app.utils.auth import get_current_user
from typing import List
from app.services.email_service import send_email
from app.models.car import Car

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.post("/", response_model=AppointmentResponseSchema)
async def create_appointment(appointment: AppointmentCreateSchema, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Check if the car belongs to the user
    car = db.query(Car).filter(Car.id == appointment.car_id, Car.user_id == current_user.id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Автомобіль не знайдено або не належить вам")
    
    new_appointment = Appointment(user_id=current_user.id, **appointment.model_dump())
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    # Send email (asynchronously)
    try:
        await send_email(
            to_email=current_user.email,
            subject="Підтвердження запису на обслуговування",
            message=f"Ваш запис на {new_appointment.appointment_date} створено!"
        )
    except Exception:
        pass
    return new_appointment

@router.get("/", response_model=List[AppointmentResponseSchema])
async def get_appointments(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Appointment).filter(Appointment.user_id == current_user.id).all()

@router.get("/my", response_model=List[AppointmentResponseSchema])
async def get_my_appointments(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "mechanic":
        raise HTTPException(status_code=403, detail="Тільки механік може переглядати свої записи")
    return db.query(Appointment).filter(Appointment.mechanic_id == current_user.id).all()

@router.get("/history", response_model=List[AppointmentResponseSchema])
async def get_appointment_history(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Get all appointment history for the customer (including completed ones)"""
    return db.query(Appointment).filter(Appointment.user_id == current_user.id).order_by(Appointment.appointment_date.desc()).all()

@router.put("/{appointment_id}", response_model=AppointmentResponseSchema)
async def update_appointment(appointment_id: int, appointment: AppointmentCreateSchema, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Запис не знайдено")
    if db_appointment.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Немає доступу")
    
    # Check if the car belongs to the user (if changing)
    if appointment.car_id != db_appointment.car_id:
        car = db.query(Car).filter(Car.id == appointment.car_id, Car.user_id == current_user.id).first()
        if not car:
            raise HTTPException(status_code=404, detail="Автомобіль не знайдено або не належить вам")
    
    # Update fields except user_id
    appointment_data = appointment.model_dump()
    for key, value in appointment_data.items():
        setattr(db_appointment, key, value)
    
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@router.delete("/{appointment_id}")
async def delete_appointment(appointment_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Запис не знайдено")
    if db_appointment.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Немає доступу")
    db.delete(db_appointment)
    db.commit()
    return {"detail": "Запис видалено"}

@router.patch("/{appointment_id}/assign_mechanic")
async def assign_mechanic(appointment_id: int, mechanic_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Тільки адміністратор може призначати механіка")
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Запис не знайдено")
    db_appointment.mechanic_id = mechanic_id
    db.commit()
    db.refresh(db_appointment)
    return {"detail": "Механіка призначено"}

@router.patch("/{appointment_id}/status")
async def update_appointment_status(appointment_id: int, status: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Update appointment status (only admin or appointment owner)"""
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Запис не знайдено")
    
    # Check access rights
    if db_appointment.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Немає доступу")
    
    # Validate status
    valid_statuses = ["Заплановано", "В роботі", "Завершено", "Скасовано"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Недійсний статус. Дозволені: {', '.join(valid_statuses)}")
    
    db_appointment.status = status
    db.commit()
    db.refresh(db_appointment)
    return {"detail": f"Статус запису змінено на '{status}'", "appointment": db_appointment}
