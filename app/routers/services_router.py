from fastapi import APIRouter, Depends, HTTPException
from app.models.service import Service
from app.schemas.service_schema import ServiceCreateSchema, ServiceResponseSchema
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.database import get_db
from typing import List
from app.utils.auth import admin_required

router = APIRouter(prefix="/services", tags=["Services"])

@router.post("/", response_model=ServiceResponseSchema)
async def create_service(service: ServiceCreateSchema, db: AsyncSession = Depends(get_db), current_user=Depends(admin_required)):
    new_service = Service(**service.model_dump())
    db.add(new_service)
    await db.commit()
    await db.refresh(new_service)
    return new_service

@router.get("/", response_model=List[ServiceResponseSchema])
async def get_all_services(db: AsyncSession = Depends(get_db)):
    from sqlalchemy.future import select
    result = await db.execute(select(Service))
    return result.scalars().all()

@router.put("/{service_id}", response_model=ServiceResponseSchema)
async def update_service(service_id: int, service: ServiceCreateSchema, db: AsyncSession = Depends(get_db), current_user=Depends(admin_required)):
    from sqlalchemy.future import select
    result = await db.execute(select(Service).where(Service.id == service_id))
    db_service = result.scalar_one_or_none()
    if not db_service:
        raise HTTPException(status_code=404, detail="Послугу не знайдено")
    for key, value in service.model_dump().items():
        setattr(db_service, key, value)
    await db.commit()
    await db.refresh(db_service)
    return db_service

@router.delete("/{service_id}")
async def delete_service(service_id: int, db: AsyncSession = Depends(get_db), current_user=Depends(admin_required)):
    from sqlalchemy.future import select
    result = await db.execute(select(Service).where(Service.id == service_id))
    db_service = result.scalar_one_or_none()
    if not db_service:
        raise HTTPException(status_code=404, detail="Послугу не знайдено")
    await db.delete(db_service)
    await db.commit()
    return {"detail": "Послугу видалено"}
