from typing import Literal
from app.schemas.base_schema import BaseSchema
from pydantic import EmailStr, field_validator
from app.utils.password import validate_password_schema

class UserCreateSchema(BaseSchema):
    name: str
    email: EmailStr
    password: str
    role: Literal["admin", "customer", "mechanic"]

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

class Token(BaseSchema):
    """Schema for JWT tokens (access and refresh)."""
    access_token: str
    refresh_token: str
    token_type: str

class TokenResponse(BaseSchema):
    """Response schema for returning tokens."""
    tokens: Token

class LoginRequest(BaseSchema):
    """Request schema for user login."""
    email: EmailStr
    password: str

class LogoutResponse(BaseSchema):
    """Response schema for logout endpoint."""
    message: str

class PasswordResetRequest(BaseSchema):
    """Request schema for password recovery (forgot password)."""
    email: EmailStr

class PasswordReset(BaseSchema):
    """Request schema for resetting the password using a token."""
    token: str
    new_password: str
