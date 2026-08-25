from logging.config import fileConfig

from alembic import context
from sqlmodel import SQLModel

from app.core.config import settings
from app.models import Todo, User  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    raise RuntimeError("Offline migrations are not configured for this project.")


def run_migrations_online() -> None:
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
