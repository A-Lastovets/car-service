from fastapi import APIRouter, Depends, HTTPException
from app.models.car import Car
from app.schemas.car_schema import CarCreateSchema, CarResponseSchema
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.utils.auth import get_current_user
from typing import List

router = APIRouter(prefix="/cars", tags=["Cars"])

@router.post("/", response_model=CarResponseSchema)
async def create_car(car: CarCreateSchema, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    new_car = Car(user_id=current_user.id, **car.model_dump())
    db.add(new_car)
    db.commit()
    db.refresh(new_car)
    return new_car

@router.get("/", response_model=List[CarResponseSchema])
async def get_user_cars(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Car).filter(Car.user_id == current_user.id).all()

@router.put("/{car_id}", response_model=CarResponseSchema)
async def update_car(car_id: int, car: CarCreateSchema, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_car = db.query(Car).filter(Car.id == car_id, Car.user_id == current_user.id).first()
    if not db_car:
        raise HTTPException(status_code=404, detail="Автомобіль не знайдено")
    for key, value in car.model_dump().items():
        setattr(db_car, key, value)
    db.commit()
    db.refresh(db_car)
    return db_car

@router.delete("/{car_id}")
async def delete_car(car_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_car = db.query(Car).filter(Car.id == car_id, Car.user_id == current_user.id).first()
    if not db_car:
        raise HTTPException(status_code=404, detail="Автомобіль не знайдено")
    db.delete(db_car)
    db.commit()
    return {"detail": "Автомобіль видалено"}
