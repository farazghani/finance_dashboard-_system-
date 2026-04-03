from pydantic import BaseModel , EmailStr , Field , ConfigDict
from enum import Enum
from typing import Optional
from datetime import datetime

class Role(str , Enum):
    viewer = "viewer"
    analyst = "analyst"
    admin = "admin"

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[Role] = None


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

    model_config = ConfigDict(from_attributes=True)


