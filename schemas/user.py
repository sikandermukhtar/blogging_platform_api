from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr = Field(..., max_length=50)
    password: str = Field(..., min_length=8, max_length=20)
    name: str = Field(..., min_length=3, max_length=35)


class UserRead(BaseModel):
    id: int
    email: str
    name: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    role_id: int

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None


class UserRoleUpdate(BaseModel):
    role_id: int = Field(
        ..., examples=["1 for admin, 3 for mod, 4 for author, 5 by default for user."]
    )


class UserLogin(BaseModel):
    email: EmailStr = Field(..., max_length=50)
    password: str = Field(..., min_length=8, max_length=20)


class UserLoginSuccess(BaseModel):
    user: UserRead
    message: str
    access_token: str
    token_type: str
