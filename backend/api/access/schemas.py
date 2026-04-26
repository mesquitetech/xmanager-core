from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class AccessLogBase(BaseModel):
    site_id: UUID
    check_in_time: datetime
    check_out_time: Optional[datetime] = None
    purpose: str
    activities: Optional[str] = None
    photos: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class AccessLogCreate(AccessLogBase):
    pass

class AccessLogUpdate(BaseModel):
    check_out_time: Optional[datetime] = None
    activities: Optional[str] = None
    photos: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class AccessLog(AccessLogBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Include user information
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    
    # Include site information
    site_name: Optional[str] = None
    site_code: Optional[str] = None
    
    class Config:
        from_attributes = True

class AccessLogList(BaseModel):
    items: List[AccessLog]
    total: int
    page: int
    size: int
    pages: int
