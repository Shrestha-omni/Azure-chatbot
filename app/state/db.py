# app/state/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base,Session
from app.config.settings import settings
from typing import Generator
# SQLite engine
engine = create_engine(
    settings.sqlite_path, 
    connect_args={"check_same_thread": False}  # required for SQLite multithreading
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for ORM models
Base = declarative_base()


# Dependency for FastAPI
def get_db() -> Generator[Session, None, None]:
    """
    Yield a database session for use with FastAPI dependencies.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
