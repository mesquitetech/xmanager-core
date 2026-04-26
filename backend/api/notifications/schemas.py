"""
Pydantic schemas for notification API endpoints
"""

from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class NotificationBase(BaseModel):
    title: str
    message: str
    notification_type: str = "info"
    priority: str = "normal"
    target_role: Optional[str] = None
    related_id: Optional[UUID] = None
    related_table: Optional[str] = None
    expires_at: Optional[datetime] = None
    meta_data: Optional[Dict[str, Any]] = None

class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    notification_type: Optional[str] = None
    priority: Optional[str] = None
    target_role: Optional[str] = None
    expires_at: Optional[datetime] = None
    meta_data: Optional[Dict[str, Any]] = None

class NotificationResponse(NotificationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_by_id: Optional[UUID] = None
    created_at: datetime
    is_system_generated: bool = False
    is_read: Optional[bool] = False
    read_at: Optional[datetime] = None
    is_dismissed: Optional[bool] = False

class UserNotificationUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_dismissed: Optional[bool] = None

class NotificationList(BaseModel):
    notifications: List[NotificationResponse]
    unread_count: int
    total_returned: int

class CreateNotificationRequest(BaseModel):
    notification_type: str
    title: str
    message: str
    priority: str = "normal"
    target_roles: List[str]
    expires_at: Optional[datetime] = None
    related_id: Optional[UUID] = None
    related_table: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None

class NotificationCounts(BaseModel):
    total: int
    unread: int
    by_priority: Dict[str, int]
    by_type: Dict[str, int]