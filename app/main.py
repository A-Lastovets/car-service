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
from app.middlewares.middlewares import setup_middlewares
from app.services.init_admin import create_initial_admin, create_initial_admin_mechanic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle resources"""
    try:
        # Initialize admin users if they don't exist
        logger.info("🔧 Checking for initial admin users...")
        await create_initial_admin()
        await create_initial_admin_mechanic()
        logger.info("✅ Admin initialization completed")

        yield

    except Exception as e:
        logger.error(f"❌ Error during server startup: {e}")
        raise e

    finally:
        logger.info("🔴 Application shutdown complete")

app = FastAPI(
    lifespan=lifespan,
    title="Car Service API",
    description="API for managing car service appointments",
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

logger.info("✅ Car Service API successfully started!")
