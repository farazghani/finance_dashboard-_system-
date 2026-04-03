from pydantic import BaseModel , EmailStr , Field
from enum import Enum
from typing import Optional
from datetime import datetime

class Role(str , Enum):
    viewer = "viewer"
    analyst = "analyst"
    admin = "admin"


class UserBase(BaseModel):
    name : str = Field(... , min_length=2,max_length=50)
    email : EmailStr
    role: Role

class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


