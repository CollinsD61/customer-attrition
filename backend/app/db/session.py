from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.core.config import settings
from backend.app.db.base import Base

_engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def get_db() -> Generator[Session, None, None]:
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    Base.metadata.create_all(bind=_engine)
