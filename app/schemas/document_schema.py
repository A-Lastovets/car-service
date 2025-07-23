from app.schemas.base_schema import BaseSchema
from typing import Literal

class DocumentCreateSchema(BaseSchema):
    mechanic_id: int
    type: Literal["паспорт", "ІПН", "диплом", "договір"]
    file_path: str

class DocumentResponseSchema(BaseSchema):
    id: int
    mechanic_id: int
    type: str
    file_path: str

    class Config:
        from_attributes = True
