from app.schemas.base_schema import BaseSchema
from typing import Literal
from datetime import date

class MechanicCreateSchema(BaseSchema):
    name: str
    birth_date: date
    login: str
    password: str
    role: Literal["admin", "mechanic"]
    position: str

class MechanicLoginSchema(BaseSchema):
    login: str
    password: str

class MechanicResponseSchema(BaseSchema):
    id: int
    name: str
    birth_date: date
    login: str
    role: str
    position: str

    class Config:
        from_attributes = True
