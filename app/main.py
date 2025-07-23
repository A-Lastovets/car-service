import logging
from fastapi import FastAPI
from app.routers.auth_router import router as auth_router
from app.routers.users_router import router as users_router
from app.routers.cars_router import router as cars_router
from app.routers.services_router import router as services_router
from app.routers.mechanics_router import router as mechanics_router
from app.routers.documents_router import router as documents_router
from app.routers.appointments_router import router as appointments_router
from app.routers.admin_router import router as admin_router
from contextlib import asynccontextmanager
from logging.config import dictConfig
from app.config import LogConfig
from app.dependencies.cache import redis_client
from app.middlewares.middlewares import setup_middlewares
from app.services.init_admin import create_initial_admin, create_initial_admin_mechanic

dictConfig(LogConfig().dict())
logger = logging.getLogger("app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управління ресурсами під час життєвого циклу API"""
    try:
        redis = await redis_client.get_redis()
        if redis:
            logger.info("✅ Redis успішно підключено")
        else:
            logger.error("❌ Не вдалося підключитися до Redis!")

        # Initialize admin users if they don't exist
        logger.info("🔧 Checking for initial admin users...")
        create_initial_admin()
        create_initial_admin_mechanic()

        yield

    except Exception as e:
        logger.error(f"❌ Помилка при запуску сервера: {e}")
        raise e

    finally:
        await redis_client.close_redis()
        logger.info("🔴 Підключення до Redis закрито")

app = FastAPI(
    lifespan=lifespan,
    title="Car Service API",
    description="API для управління записами на обслуговування автомобілів",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True},
)

setup_middlewares(app)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(cars_router)
app.include_router(services_router)
app.include_router(mechanics_router)
app.include_router(documents_router)
app.include_router(appointments_router)
app.include_router(admin_router)

logger.info("✅ Service API успішно запущено!")
