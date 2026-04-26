"""
Router for settings API endpoints - Solo endpoints HTTP
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from models import User
from auth.utils import get_current_user
from services.settings_service import SettingsService
from api.settings.schemas import (
    UpdateUserProfileRequest, UpdatePasswordRequest, UserPreferenceRequest,
    ThemePreferenceRequest, NotificationPreferenceRequest,
    UserProfileResponse, UserPreferencesResponse, MessageResponse, UpdateProfileResponse
)

router = APIRouter(tags=["settings"])
    
@router.get("/user-profile", response_model=UserProfileResponse)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get the current user's profile."""
    return SettingsService.get_user_profile(current_user)

@router.post("/update-profile", response_model=UpdateProfileResponse)
async def update_user_profile(
    profile_data: UpdateUserProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the current user's profile."""
    return SettingsService.update_user_profile(db, current_user, profile_data)

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: UpdatePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change the current user's password."""
    return SettingsService.change_password(db, current_user, password_data)

@router.post("/preference", response_model=MessageResponse)
async def set_user_preference(
    preference: UserPreferenceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set a user preference."""
    return SettingsService.set_user_preference(db, str(current_user.id), preference)

@router.get("/preferences", response_model=UserPreferencesResponse)
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all preferences for the current user."""
    return SettingsService.get_user_preferences(db, str(current_user.id))

@router.post("/theme", response_model=MessageResponse)
async def set_theme_preference(
    theme_data: ThemePreferenceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set the user's theme preference."""
    return SettingsService.set_theme_preference(db, str(current_user.id), theme_data)

@router.post("/notifications", response_model=MessageResponse)
async def set_notification_preferences(
    notification_data: NotificationPreferenceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set the user's notification preferences."""
    return SettingsService.set_notification_preferences(db, str(current_user.id), notification_data)

@router.post("/logout-all", response_model=MessageResponse)
async def logout_all_devices(
    current_user: User = Depends(get_current_user)
):
    """Logout from all devices by updating the user's token version."""
    return SettingsService.logout_all_devices(current_user)