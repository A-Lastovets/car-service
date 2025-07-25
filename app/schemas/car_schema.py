from app.schemas.base_schema import BaseSchema
from pydantic import Field

class CarCreateSchema(BaseSchema):
    brand: str
    model: str
    year: int
    plate_number: str = Field(..., alias="plateNumber")
    vin: str

    class Config:
        allow_population_by_field_name = True

class CarResponseSchema(BaseSchema):
    id: int
    user_id: int
    brand: str
    model: str
    year: int
    plate_number: str
    vin: str

    class Config:
        from_attributes = True
