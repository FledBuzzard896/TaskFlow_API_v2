from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., description="Уникальное имя пользователя")
    email: EmailStr = Field(..., description="Электронная почта")
    full_name: Optional[str] = Field(None, description="Полное имя")

class UserCreate(UserBase):
    password: Optional[str] = Field(None, description="Пароль (только для этапа без Keycloak)")
    # На этапе 1 пароль можно не хранить, но для тестов пригодится

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool = True
    created_at: Optional[datetime]
    # Роли пока не добавляем, они появятся на этапе с Keycloak