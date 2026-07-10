import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Resolve the path to the backend/.env file relative to database.py location
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dotenv_path = os.path.join(backend_dir, ".env")
load_dotenv(dotenv_path)

# Dynamically retrieve connection URL from environment variables, defaulting to local SQLite file
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./hcp_crm.db")

# SQLite needs connect_args={"check_same_thread": False} parameter, PostgreSQL does not
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
