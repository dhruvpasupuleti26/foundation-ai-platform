"""Alembic environment configuration."""

from __future__ import annotations

from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

from llm_platform.database.models import Base
from llm_platform.schemas.config import PlatformConfig
from llm_platform.utils.config_loader import ConfigLoader

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _resolve_database_url() -> str:
    explicit_url = config.get_main_option("sqlalchemy.url")
    if explicit_url:
        return explicit_url
    config_path = config.get_main_option("platform_config_path") or str(Path("configs/platform.yaml"))
    platform_config = ConfigLoader().load(config_path, PlatformConfig)
    return platform_config.database.sqlalchemy_url


def run_migrations_offline() -> None:
    context.configure(
        url=_resolve_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    alembic_config = config.get_section(config.config_ini_section, {})
    alembic_config["sqlalchemy.url"] = _resolve_database_url()
    connectable = engine_from_config(
        alembic_config,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
