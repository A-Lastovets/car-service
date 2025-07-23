import jwt
from datetime import datetime, timedelta
from typing import Any, Optional
from fastapi import HTTPException, status
from app.config import config

# Get current UTC time
def get_utc_now():
    """Get current UTC time."""
    return datetime.utcnow()

# Create JWT token
def create_access_token(user: Any):
    """Creates a JWT token containing all user information."""
    expires_delta = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Check if it's a User or Mechanic object
    if hasattr(user, 'email'):  # User object
        to_encode = {
            "id": str(user.id),
            "name": user.full_name,
            "email": user.email,
            "role": user.role,
            "type": "user",
            "exp": get_utc_now() + expires_delta,
        }
    else:  # Mechanic object
        to_encode = {
            "id": str(user.id),
            "name": user.full_name,
            "email": user.email,
            "role": "mechanic",
            "type": "mechanic",
            "exp": get_utc_now() + expires_delta,
        }

    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)


# Create refresh JWT token
def create_refresh_token(user: Any):
    """Creates a long-term refresh_token containing user information."""
    expires_delta = timedelta(days=7)  # 7 days for refresh token

    # Check if it's a User or Mechanic object
    if hasattr(user, 'email'):  # User object
        to_encode = {
            "id": str(user.id),
            "name": user.full_name,
            "email": user.email,
            "role": user.role,
            "type": "user",
            "exp": get_utc_now() + expires_delta,
        }
    else:  # Mechanic object
        to_encode = {
            "id": str(user.id),
            "name": user.full_name,
            "email": user.email,
            "role": "mechanic",
            "type": "mechanic",
            "exp": get_utc_now() + expires_delta,
        }

    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)


# Create password reset token
def create_password_reset_token(email: str):
    """Creates a password reset token with expiration time."""
    expires_delta = timedelta(minutes=15)  # 15 minutes for password reset
    
    to_encode = {
        "sub": email,
        "exp": get_utc_now() + expires_delta,
        "type": "password_reset",
    }

    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)


# Single function for decoding tokens (access and refresh)
def decode_jwt_token(token: str):
    """Decodes JWT token and returns all its data"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])

        # Check token type
        token_type = payload.get("type", "user")  # Default to user for backward compatibility
        
        # If this is a password reset token
        if token_type == "password_reset":
            email = payload.get("sub")
            if not email:
                raise credentials_exception
            return {"email": email, "type": "password_reset"}

        # Get all data from user token
        if token_type == "user":
            user_data = {
                "id": payload.get("id"),
                "name": payload.get("name"),
                "email": payload.get("email"),
                "role": payload.get("role"),
                "type": "user"
            }
        elif token_type == "mechanic":
            user_data = {
                "id": payload.get("id"),
                "name": payload.get("name"),
                "email": payload.get("email"),
                "role": "mechanic",
                "type": "mechanic"
            }
        else:
            raise credentials_exception

        # Validate required fields
        if not all([user_data["id"], user_data["email"], user_data["role"]]):
            raise credentials_exception

        return user_data

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise credentials_exception


# Verify password reset token
def verify_password_reset_token(token: str) -> Optional[str]:
    """Verifies password reset token and returns email if valid."""
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        
        if payload.get("type") != "password_reset":
            return None
            
        email = payload.get("sub")
        if not email:
            return None
            
        return email
        
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None
