import os
import asyncio
from logging.config import fileConfig
from dotenv import load_dotenv
from sqlalchemy import create_engine

from sqlalchemy.pool import NullPool

from alembic import context
from app.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.

load_dotenv()

USER = os.getenv("POSTGRES_USER")
PWD = os.getenv("POSTGRES_PASSWORD")
HOST = os.getenv("POSTGRES_HOST")
PORT = os.getenv("DATABASE_PORT")
DB = os.getenv("POSTGRES_DB")

ALEMBIC_DATABASE_URL = f"postgresql://{USER}:{PWD}@{HOST}:{PORT}/{DB}"


config = context.config

config.set_main_option("sqlalchemy.url", ALEMBIC_DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=ALEMBIC_DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:

    try:
        connectable = create_engine(
            ALEMBIC_DATABASE_URL,
            poolclass=NullPool,
            connect_args={"sslmode": "require"}
        )
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
            )
            with context.begin_transaction():
                context.run_migrations()
    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
        raise

# Run the appropriate function

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
