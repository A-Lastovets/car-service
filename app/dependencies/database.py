from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import config

# Configure engine with MySQL-specific settings
engine = create_async_engine(
    config.DATABASE_URL,
    echo=True,
    future=True,
    # MySQL-specific connection arguments
    connect_args={
        "charset": "utf8mb4",
        "autocommit": False,
        "ssl": False,
    },
    # Pool settings for better performance
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_db():
    async with SessionLocal() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
