from __future__ import annotations

from app.core.config import get_settings


def create_engine_and_sessionmaker():
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Install SQLAlchemy to use the PostgreSQL database layer.") from exc
    engine = create_engine(get_settings().database_url, pool_pre_ping=True)
    return engine, sessionmaker(bind=engine, autoflush=False, autocommit=False)
