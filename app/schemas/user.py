from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Schema base para usuário"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema para criação de usuário (registro)"""
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    """Schema para login de usuário"""
    username: str
    password: str


class UserResponse(UserBase):
    """Schema de resposta com informações do usuário"""
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserInDB(UserBase):
    """Schema do usuário no banco de dados"""
    id: int
    hashed_password: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
