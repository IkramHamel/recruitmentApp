# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.core.config import config
# PostgreSQL connection string
DATABASE_URL = config.DATABASE_URL  # Example: postgresql://username:password@localhost/dbname

# Create PostgreSQL engine
engine = create_engine(DATABASE_URL)
# SessionLocal for creating sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()
Base.metadata.create_all(engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

