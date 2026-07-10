from typing import Generator
from app.db.database import SessionLocal

def get_db() -> Generator:
    """Dependency injection helper to yield database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
