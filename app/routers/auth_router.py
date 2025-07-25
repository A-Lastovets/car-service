from fastapi import APIRouter, HTTPException, Depends
from app.schemas.user_schema import (
    UserCreateSchema, UserRegisterSchema, UserLoginSchema, UserResponseSchema,
    Token, TokenResponse, LoginRequest, LogoutResponse, PasswordResetRequest, PasswordReset
)
from app.models.user import User
from app.utils.auth import authenticate_user, get_user_by_email
from app.utils.tokens import create_access_token, create_refresh_token, decode_jwt_token, create_password_reset_token
from app.utils.password import get_password_hash, validate_password, update_password, validate_password_schema
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.database import get_db
from app.dependencies.cache import redis_client
from app.services.email_service import send_email
from app.config import config
import logging
from fastapi import status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.utils.tokens import get_utc_now

# Logger for authentication events
logger = logging.getLogger("auth")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/sign-in-swagger")

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponseSchema)
async def register(user: UserRegisterSchema, db: AsyncSession = Depends(get_db)):
    """Register a new customer. Role is automatically set to 'customer'."""
    from sqlalchemy.future import select
    result = await db.execute(select(User).where(User.email == user.email.lower()))
    db_user = result.scalar_one_or_none()
    if db_user:
        raise HTTPException(status_code=400, detail="Користувач уже існує")
    hashed_password = get_password_hash(user.password)
    new_user = User(
        full_name=user.name,
        email=user.email.lower(),
        hashed_password=hashed_password,
        role="customer"  # Automatically set to customer
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


# /auth/login: for frontend and API clients (JSON, not for Swagger UI)
@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is blocked or inactive",
        )
    client_ip = request.client.host
    current_time = get_utc_now()
    logger.info(
        f"User login: email={user.email}, ip={client_ip}, time={current_time}"
    )
    user.last_login = current_time
    db.add(user)
    await db.commit()
    await db.refresh(user)
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    return TokenResponse(
        tokens=Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        ),
    )


@router.post("/change-password")
async def change_password(email: str, new_password: str, db: AsyncSession = Depends(get_db)):
    validate_password(new_password)
    updated_user = await update_password(db, email, new_password)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Password updated successfully"}


@router.post("/logout", response_model=LogoutResponse, status_code=status.HTTP_200_OK)
async def logout(token: str):
    
    redis = await redis_client.get_redis()
    
    if await redis.exists(f"blacklist:{token}"):
        raise HTTPException(status_code=401, detail="Token already revoked")

    try:
        decode_jwt_token(token)
    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid token")

    await redis.setex(f"blacklist:{token}", 7 * 24 * 60 * 60, "revoked")
    logger.info(f"Token revoked: {token}")

    return LogoutResponse(message="Successfully logged out")


@router.post("/password-recovery", status_code=status.HTTP_200_OK)
async def password_recovery(
    data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    """Запит на скидання пароля та надсилання email з посиланням"""
    
    user = await get_user_by_email(db, data.email)
    
    response_message = {
        "message": "If an account with that email exists, a password reset email has been sent.",
    }

    if not user:
        return response_message

    token = create_password_reset_token(user.email)
    
    redis = await redis_client.get_redis()
    await redis.setex(
        f"password-reset:{token}",
        config.RESET_TOKEN_EXPIRE_MINUTES * 60,
        user.email,
    )

    reset_link = f"{config.FRONTEND_URL}/auth/reset-password?token={token}"

    # TODO: Відправка email з посиланням для скидання пароля
    await send_email(
        to_email=user.email,
        subject="Password Reset Request",
        message=f"To reset your password, click the following link: {reset_link}",
        html=False
    )

    return response_message


# Скидання пароля (повертаємо оновлену інформацію про користувача)
@router.post("/password-reset", status_code=status.HTTP_200_OK)
async def password_reset(
    data: PasswordReset,
    db: AsyncSession = Depends(get_db),
):
    redis = await redis_client.get_redis()
    try:
        email = await redis.get(f"password-reset:{data.token}")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid or expired token")

    except Exception as e:
        logger.error(f"Error accessing Redis: {e}")
        raise HTTPException(
            status_code=500,
            detail="Temporary server issue. Try again later. Invalid or expired token.",
        )

    user = await get_user_by_email(db, email)
    if not user:
        logger.warning(f"User not found for email: {email}")
        raise HTTPException(status_code=404, detail="User not found")

    try:
        validate_password_schema(data.new_password)
    except ValueError as e:
        logger.warning(
            f"Invalid password attempt for user {email}: {e}",
        )
        raise HTTPException(status_code=400, detail=str(e))

    if not await update_password(db, user.email, data.new_password):
        logger.error(
            f"Failed to update password for user {email}",
        )  # Лог якщо пароль не змінився
        raise HTTPException(
            status_code=500,
            detail="Could not update password. Try again later.",
        )
    # Видаляємо токен тільки після успішного оновлення пароля
    await redis.delete(f"password-reset:{data.token}")

    logger.info(f"Password reset successful for {email}")
    return {"message": "Password has been reset successfully. Please log in again."}



@router.post("/refresh-token", response_model=TokenResponse, status_code=200)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """Оновлення `access_token` за допомогою `refresh_token`"""

    redis = await redis_client.get_redis()

    # Check if refresh token is blacklisted
    if await redis.exists(f"blacklist:{refresh_token}"):
        logger.warning(f"Attempt to use blacklisted refresh token: {refresh_token}")
        raise HTTPException(status_code=401, detail="Refresh token is revoked")

    token_data = decode_jwt_token(refresh_token)

    from sqlalchemy.future import select
    result = await db.execute(select(User).where(User.id == token_data["id"]))
    user = result.scalar_one_or_none()

    if not user:
        logger.warning(f"User not found for refresh token: {refresh_token}")
        raise HTTPException(status_code=404, detail="User not found")

    # Create new access token
    new_access_token = create_access_token(user)
    logger.info(f"Access token refreshed for user: {user.email} (id={user.id})")

    return TokenResponse(
        tokens=Token(
            access_token=new_access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        ),
    )


# /auth/sign-in-swagger: for Swagger UI login (OAuth2PasswordRequestForm)
@router.post(
    "/sign-in-swagger",
    status_code=status.HTTP_200_OK,
    tags=["Authentication"],
)
async def sign_in_swagger(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    current_time = get_utc_now()
    user.last_login = current_time
    db.add(user)
    await db.commit()
    await db.refresh(user)
    access_token = create_access_token(user)
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
