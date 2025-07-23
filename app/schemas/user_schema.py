from typing import Literal
from app.schemas.base_schema import BaseSchema
from pydantic import EmailStr, field_validator
from app.utils.password import validate_password_schema

class UserCreateSchema(BaseSchema):
    name: str
    email: EmailStr
    password: str
    role: Literal["admin", "customer"]

    @field_validator("password")
    def password_validation(cls, v):
        return validate_password_schema(v)

class UserRegisterSchema(BaseSchema):
    name: str
    email: EmailStr
    password: str

    @field_validator("password")
    def password_validation(cls, v):
        return validate_password_schema(v)

class UserLoginSchema(BaseSchema):
    email: EmailStr
    password: str

class UserResponseSchema(BaseSchema):
    id: int
    full_name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True
