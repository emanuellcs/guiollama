import logging
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from adapters.orm import Base
from infra.config import get_settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# Override sqlalchemy.url with app settings
settings = get_settings()

# Ensure SQLite directory exists
if settings.DATABASE_URL.startswith("sqlite"):
    db_path = settings.DATABASE_URL.split("://")[-1]
    # Adjust for absolute paths if needed, though split handles basic cases
    # For "sqlite:///./data/guiollama.db", part is "/./data/guiollama.db" or "./data..." depending on split
    # Let's rely on standard path manipulation:
    if "sqlite:///" in settings.DATABASE_URL:
        # relative: sqlite:///foo.db -> foo.db
        # absolute: sqlite:////foo.db -> /foo.db
        real_path = settings.DATABASE_URL.replace("sqlite:///", "")

        # If it is relative (starts with .) or absolute, check dir
        if ":memory:" not in real_path:
            # Handle the specific ./data/ case cleanly
            if real_path.startswith("./"):
                real_path = real_path[2:]  # remove ./
                real_path = os.path.abspath(real_path)

            db_dir = os.path.dirname(real_path)
            if db_dir and not os.path.exists(db_dir):
                print(f"Creating database directory for migration: {db_dir}")
                os.makedirs(db_dir, exist_ok=True)

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
