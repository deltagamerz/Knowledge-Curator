# backend/app/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

# Railway injects the database connection string as an environment variable called 'DATABASE_URL'.
# We also provide a default fallback for local development if we want to use a local DB.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local_test.db")

# The create_engine function is the entry point to the database.
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Each instance of SessionLocal will be a new database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# We will inherit from this class to create each of the database models (ORM classes).
Base = declarative_base()