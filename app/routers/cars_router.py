from fastapi import APIRouter, Depends, HTTPException
from app.models.car import Car
from app.schemas.car_schema import CarCreateSchema, CarResponseSchema
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.database import get_db
from app.utils.auth import role_required_with_cache
from typing import List

router = APIRouter(prefix="/cars", tags=["Cars"])

@router.post("/", response_model=CarResponseSchema)
async def create_car(car: CarCreateSchema, db: AsyncSession = Depends(get_db), current_user=Depends(role_required_with_cache(["customer", "admin"]))):
    new_car = Car(user_id=current_user.id, **car.model_dump())
    db.add(new_car)
    await db.commit()
    await db.refresh(new_car)
    return new_car

@router.get("/", response_model=List[CarResponseSchema])
async def get_user_cars(db: AsyncSession = Depends(get_db), current_user=Depends(role_required_with_cache(["customer", "admin"]))):
    from sqlalchemy.future import select
    result = await db.execute(select(Car).where(Car.user_id == current_user.id))
    return result.scalars().all()

@router.put("/{car_id}", response_model=CarResponseSchema)
async def update_car(car_id: int, car: CarCreateSchema, db: AsyncSession = Depends(get_db), current_user=Depends(role_required_with_cache(["customer", "admin"]))):
    from sqlalchemy.future import select
    result = await db.execute(select(Car).where(Car.id == car_id, Car.user_id == current_user.id))
    db_car = result.scalar_one_or_none()
    if not db_car:
        raise HTTPException(status_code=404, detail="Автомобіль не знайдено")
    for key, value in car.model_dump().items():
        setattr(db_car, key, value)
    await db.commit()
    await db.refresh(db_car)
    return db_car

@router.delete("/{car_id}")
async def delete_car(car_id: int, db: AsyncSession = Depends(get_db), current_user=Depends(role_required_with_cache(["customer", "admin"]))):
    from sqlalchemy.future import select
    result = await db.execute(select(Car).where(Car.id == car_id, Car.user_id == current_user.id))
    db_car = result.scalar_one_or_none()
    if not db_car:
        raise HTTPException(status_code=404, detail="Автомобіль не знайдено")
    await db.delete(db_car)
    await db.commit()
    return {"detail": "Автомобіль видалено"}
