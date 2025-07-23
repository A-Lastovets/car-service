from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple
import uuid
import logging

from fastapi import HTTPException, status
from jose import ExpiredSignatureError, JWTError, jwt

from app.config import config

logger = logging.getLogger(__name__)

def get_utc_now():
    return datetime.now(timezone.utc)

# Create JWT token
def create_access_token(user: Any):
    """Creates a JWT token containing all user information."""
    expires_delta = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Check if it's a User or Mechanic object
    if hasattr(user, 'email'):  # User object
        to_encode = {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "type": "user",
            "exp": get_utc_now() + expires_delta,
        }
    else:  # Mechanic object
        to_encode = {
            "id": str(user.id),
            "name": user.name,
            "login": user.login,
            "role": user.role,
            "type": "mechanic",
            "exp": get_utc_now() + expires_delta,
        }

    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)


# Create refresh JWT token
def create_refresh_token(user: Any):
    """Creates a long-term refresh_token containing user information."""
    expires_delta = timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)

    # Check if it's a User or Mechanic object
    if hasattr(user, 'email'):  # User object
        to_encode = {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "type": "user",
            "exp": get_utc_now() + expires_delta,
        }
    else:  # Mechanic object
        to_encode = {
            "id": str(user.id),
            "name": user.name,
            "login": user.login,
            "role": user.role,
            "type": "mechanic",
            "exp": get_utc_now() + expires_delta,
        }

    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)


# Create password reset token
def create_password_reset_token(email: str):
    """Creates a password reset token with expiration time."""
    expires_delta = timedelta(minutes=config.RESET_TOKEN_EXPIRE_MINUTES)
    
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
                "type": "user",
                "exp": payload.get("exp"),
            }
        else:  # mechanic
            user_data = {
                "id": payload.get("id"),
                "name": payload.get("name"),
                "login": payload.get("login"),
                "role": payload.get("role"),
                "type": "mechanic",
                "exp": payload.get("exp"),
            }

        # Make sure all key fields are in the token
        if None in user_data.values():
            raise credentials_exception

        # Check if role is valid
        if user_data["role"] not in ["customer", "mechanic", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid user role",
            )

        return user_data

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")

    except JWTError:
        raise credentials_exception
