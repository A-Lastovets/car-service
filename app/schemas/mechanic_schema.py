from app.schemas.base_schema import BaseSchema
from typing import Literal
from datetime import date, datetime

class MechanicCreateSchema(BaseSchema):
    email: str
    password: str
    full_name: str
    phone: str | None = None
    specialization: str | None = None

class MechanicLoginSchema(BaseSchema):
    email: str
    password: str

class MechanicResponseSchema(BaseSchema):
    id: int
    email: str
    full_name: str
    phone: str | None
    specialization: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
