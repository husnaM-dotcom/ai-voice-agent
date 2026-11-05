
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Locate the backend directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Database location
DATABASE_URL = f"sqlite:///{BASE_DIR / 'car_rental.db'}"

# Create the database engine
engine = create_engine(
    DATABASE_URL,
    echo=True
)

# Create a session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)
