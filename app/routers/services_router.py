from fastapi import APIRouter, Depends, HTTPException
from app.models.service import Service
from app.schemas.service_schema import ServiceCreateSchema, ServiceResponseSchema
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from typing import List
from app.utils.auth import get_current_user

router = APIRouter(prefix="/services", tags=["Services"])

@router.post("/", response_model=ServiceResponseSchema)
async def create_service(service: ServiceCreateSchema, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Тільки адміністратор може створювати послуги")
    new_service = Service(**service.model_dump())
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return new_service

@router.get("/", response_model=List[ServiceResponseSchema])
async def get_all_services(db: Session = Depends(get_db)):
    return db.query(Service).all()

@router.put("/{service_id}", response_model=ServiceResponseSchema)
async def update_service(service_id: int, service: ServiceCreateSchema, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Тільки адміністратор може змінювати послуги")
    db_service = db.query(Service).filter(Service.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Послугу не знайдено")
    for key, value in service.model_dump().items():
        setattr(db_service, key, value)
    db.commit()
    db.refresh(db_service)
    return db_service

@router.delete("/{service_id}")
async def delete_service(service_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Тільки адміністратор може видаляти послуги")
    db_service = db.query(Service).filter(Service.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Послугу не знайдено")
    db.delete(db_service)
    db.commit()
    return {"detail": "Послугу видалено"}
