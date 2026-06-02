"""SQLAlchemy engine and session management."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from llm_platform.schemas.config import DatabaseConfig


class DatabaseSessionManager:
    """Create SQLAlchemy engines and transactional sessions from config."""

    def __init__(self, config: DatabaseConfig) -> None:
        self._config = config
        self._ensure_sqlite_directory()
        self._engine = create_engine(config.sqlalchemy_url, echo=config.echo, future=True)
        self._session_factory = sessionmaker(bind=self._engine, class_=Session, expire_on_commit=False)

    @property
    def engine(self) -> Engine:
        return self._engine

    @property
    def url(self) -> str:
        return self._config.sqlalchemy_url

    @contextmanager
    def session_scope(self) -> Iterator[Session]:
        session = self._session_factory()
        try:
            yield session
        finally:
            session.close()

    def _ensure_sqlite_directory(self) -> None:
        if self._config.engine.lower() != "sqlite":
            return
        database_path = Path(self._config.path)
        if database_path.parent != Path("."):
            database_path.parent.mkdir(parents=True, exist_ok=True)
