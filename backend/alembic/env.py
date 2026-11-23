from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import cấu hình database
from app.core.config import get_settings

# Import SQLAlchemy Base
from app.db.base import Base

# Import models để Alembic nhận diện bảng
import app.models


# Alembic Config
config = context.config

# Đọc DATABASE_URL từ .env
settings = get_settings()

config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL.replace("%", "%%")
)

# Cấu hình logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# SQLAlchemy metadata
target_metadata = Base.metadata


def run_migrations_offline():
    """Chạy migration không cần kết nối database."""

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Chạy migration với kết nối MySQL."""

    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {}
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()