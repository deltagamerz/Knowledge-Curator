# backend/app/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    email: str
    password: str

class User(BaseModel):
    id: int
    email: str
    
    class Config:
        orm_mode = True # New name is from_attributes=True

class Token(BaseModel):
    access_token: str
    token_type: str