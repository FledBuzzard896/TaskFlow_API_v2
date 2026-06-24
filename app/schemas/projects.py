from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProjectBase(BaseModel):
    name: str = Field(..., description="Название проекта")
    description: Optional[str] = Field(None, description="Описание проекта")

class ProjectCreate(ProjectBase):
    # На этапе 1 owner_id можно сделать опциональным, позже он будет обязательным
    owner_id: Optional[int] = Field(None, description="ID владельца проекта")

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: int
    owner_id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]