"""
Schemas para settings - Validaciones y modelos Pydantic
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class UpdateUserProfileRequest(BaseModel):
    """Request model for updating user profile."""
    full_name: Optional[str] = None
    
class UpdatePasswordRequest(BaseModel):
    """Request model for updating user password."""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)
    
class UserPreferenceRequest(BaseModel):
    """Request model for updating user preferences."""
    key: str = Field(..., min_length=1)
    value: str
    
class ThemePreferenceRequest(BaseModel):
    """Request model for updating theme preferences."""
    theme: str = Field(..., pattern="^(light|dark|auto)$")
    
class NotificationPreferenceRequest(BaseModel):
    """Request model for updating notification preferences."""
    email_notifications: bool = False
    browser_notifications: bool = False
    notify_incidents: bool = False
    notify_maintenance: bool = False
    notify_site_changes: bool = False

# Response schemas
class UserProfileResponse(BaseModel):
    """Response model for user profile."""
    id: str
    email: str
    full_name: Optional[str]
    role: Optional[str]
    created_at: Optional[str]
    last_login: Optional[str] = None
    
    class Config:
        from_attributes = True

class UserPreferencesResponse(BaseModel):
    """Response model for user preferences."""
    preferences: Dict[str, str]
    
class MessageResponse(BaseModel):
    """Standard message response."""
    message: str
    
class UpdateProfileResponse(BaseModel):
    """Response for profile update."""
    message: str
    user: Dict[str, Any]