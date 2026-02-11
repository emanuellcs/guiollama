import logging
import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from infra.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# Check for check_same_thread ONLY for SQLite
connect_args = {}

# Ensure SQLite directory exists
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

    # Simple parsing to get the file path from sqlite:///./path/to/db
    # We strip 'sqlite:///' or 'sqlite://'
    if "://" in settings.DATABASE_URL:
        db_path = settings.DATABASE_URL.split("://")[-1]
        # remove leading slash if it was 4 slashes (absolute path) vs 3 (relative)
        # simplistic check for the default config "sqlite:///./data/..."
        if settings.DATABASE_URL.startswith("sqlite:////") and not db_path.startswith("/"):
            db_path = "/" + db_path

        # If it's not memory, ensure dir exists
        if ":memory:" not in db_path:
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                logger.info(f"Creating database directory: {db_dir}")
                os.makedirs(db_dir, exist_ok=True)

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency generator for database sessions.
    Usage: with get_db() as db: ...
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize DB tables (useful for dev/testing without migrations).
    In production, use Alembic.
    """
    from adapters.orm import Base

    Base.metadata.create_all(bind=engine)
