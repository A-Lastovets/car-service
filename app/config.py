import os
from pydantic_settings import BaseSettings
from typing import Optional, List, Any

class DatabaseSettings(BaseSettings):
    DATABASE_URL: str
    DB_ECHO: bool = True

class EmailSettings(BaseSettings):
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None
    class Config:
        env_file = ".env"
        extra = "allow"

class FrontendSettings(BaseSettings):
    FRONTEND_URL: Optional[str] = None
    FRONTEND_SIGNUP_URL: Optional[str] = None

class RedisSettings(BaseSettings):
    REDIS_PASSWORD: str = ""
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: Optional[str] = None
    REDIS_USE_SSL: bool = False
    class Config:
        env_file = ".env"

class AppSettings(DatabaseSettings, RedisSettings, FrontendSettings, EmailSettings):
    ALLOWED_ORIGINS: str = "*"
    CORS_ALLOW_ALL: bool = True
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    RESET_TOKEN_EXPIRE_MINUTES: int = 30
    ENVIRONMENT: str = "development"

    @property
    def allowed_origins(self) -> List[str]:
        if self.CORS_ALLOW_ALL:
            return ["*"]
        origins = []
        if self.FRONTEND_URL:
            origins.append(self.FRONTEND_URL)
        if self.ALLOWED_ORIGINS and self.ALLOWED_ORIGINS != "*":
            origins.extend([origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")])
        return list(set(origins))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.REDIS_URL:
            if self.REDIS_PASSWORD:
                self.REDIS_URL = f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
            else:
                self.REDIS_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    class Config:
        env_file = ".env"
        extra = "allow"

class LogConfig(BaseSettings):
    LOGGER_NAME: str = "app"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    version: int = 1
    disable_existing_loggers: bool = False
    formatters: dict[str, Any] = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers: dict[str, Any] = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }
    loggers: dict[str, Any] = {
        LOGGER_NAME: {"handlers": ["default"], "level": LOG_LEVEL},
    }

config = AppSettings()
