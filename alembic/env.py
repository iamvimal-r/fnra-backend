import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, create_engine, text
from sqlalchemy.engine import make_url
from alembic import context
from dotenv import load_dotenv

load_dotenv()

# Add project root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, DATABASE_URL
from app import models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_sync_url() -> str:
    """Ensure Alembic uses synchronous pymysql driver even if DATABASE_URL is set to asyncmy."""
    url = os.environ.get("DATABASE_URL", DATABASE_URL)
    if url and "mysql+asyncmy://" in url:
        url = url.replace("mysql+asyncmy://", "mysql+pymysql://")
    return url


def ensure_database_exists(db_url: str):
    if not db_url or "sqlite" in db_url:
        return
    try:
        url_obj = make_url(db_url)
        db_name = url_obj.database
        if db_name:
            server_url = url_obj.set(database="")
            temp_engine = create_engine(server_url, isolation_level="AUTOCOMMIT")
            with temp_engine.connect() as conn:
                conn.execute(
                    text(
                        f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
                    )
                )
            temp_engine.dispose()
    except Exception:
        pass


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_sync_url()
    ensure_database_exists(url)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    db_url = get_sync_url()
    ensure_database_exists(db_url)
    configuration["sqlalchemy.url"] = db_url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
