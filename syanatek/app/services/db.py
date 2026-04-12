from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

logger = logging.getLogger(__name__)


class DatabaseService:
    def __init__(self) -> None:
        self._engine = None
        self._session_factory = None
        self.online = False

    def connect(self) -> bool:
        for attempt in range(1, settings.db_connect_retries + 1):
            try:
                self._engine = create_engine(settings.database_url, pool_pre_ping=True)
                self._session_factory = sessionmaker(bind=self._engine)
                with self._engine.connect() as connection:
                    connection.exec_driver_sql("SELECT 1")
                self.online = True
                logger.info("Connected to PostgreSQL at %s:%s", settings.db_host, settings.db_port)
                return True
            except SQLAlchemyError as exc:
                self.online = False
                logger.warning(
                    "DB connection attempt %s/%s failed: %s",
                    attempt,
                    settings.db_connect_retries,
                    exc,
                )
                time.sleep(settings.db_retry_delay_s)
        logger.error("DB unavailable. Entering offline read-only mode with demo data.")
        return False

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        if not self._session_factory:
            raise RuntimeError("Database session factory unavailable. Connect first.")
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


db_service = DatabaseService()
