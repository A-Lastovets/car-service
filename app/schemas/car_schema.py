from app.schemas.base_schema import BaseSchema

class CarCreateSchema(BaseSchema):
    brand: str
    model: str
    year: int
    plate_number: str
    vin: str

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
