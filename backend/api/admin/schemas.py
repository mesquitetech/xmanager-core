from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr
from models import UserRole

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserChangePassword(BaseModel):
    current_password: str
    new_password: str

class User(UserBase):
    id: UUID
    is_active: bool
    is_google_auth: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserList(BaseModel):
    items: List[User]
    total: int
    page: int
    size: int
    pages: int

class SystemStats(BaseModel):
    user_count: int
    site_count: int
    active_incidents: int
    open_work_orders: int
    recent_access_count: int
