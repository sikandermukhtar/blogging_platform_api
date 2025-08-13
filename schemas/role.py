from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class RoleCreate(BaseModel):
    role_name: str = Field(...)


class RoleRead(BaseModel):
    id: int
    role_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoleUpdate(BaseModel):
    role_name: str
