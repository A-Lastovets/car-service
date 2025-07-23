from app.schemas.base_schema import BaseSchema
from datetime import datetime
from typing import Optional

class AppointmentCreateSchema(BaseSchema):
    car_id: int
    service_id: int
    mechanic_id: Optional[int] = None
    appointment_date: datetime
    status: Optional[str] = "Заплановано"

class AppointmentResponseSchema(BaseSchema):
    id: int
    user_id: int
    car_id: int
    service_id: int
    mechanic_id: Optional[int]
    appointment_date: datetime
    status: str

    class Config:
        from_attributes = True
