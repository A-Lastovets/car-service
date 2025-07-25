from app.schemas.base_schema import BaseSchema

class ServiceCreateSchema(BaseSchema):
    name: str
    description: str
    price: float
    duration: int

class ServiceResponseSchema(BaseSchema):
    id: int
    name: str
    description: str
    price: float
    duration: int

    class Config:
        from_attributes = True
