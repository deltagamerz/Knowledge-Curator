# backend/app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas, auth

# --- User CRUD ---
def get_user_by_email(db: Session, email: str):
    """Reads a user from the database by their email."""
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    """Creates a new user in the database."""
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Channel CRUD (will be built out later) ---
# Placeholder for now
def get_channels_for_user(db: Session, user_id: int):
    return db.query(models.Channel).filter(models.Channel.owner_id == user_id).all()


# --- Keyword CRUD (will be built out later) ---
# Placeholder for now
def get_keywords_for_user(db: Session, user_id: int):
    return db.query(models.Keyword).filter(models.Keyword.owner_id == user_id).all()