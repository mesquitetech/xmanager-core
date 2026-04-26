"""
API Router for the notification system.
Clean architecture implementation with Router → Service → Repository pattern
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from uuid import UUID

from auth.utils import get_current_user
from db.database import get_db
from models import User
from services.notification_service import (
    get_user_notifications_logic,
    mark_notification_as_read_logic,
    dismiss_notification_logic,
    mark_all_notifications_as_read_logic,
    create_notification_logic,
    get_notification_counts_logic,
    validate_notification_id
)
from .schemas import CreateNotificationRequest, NotificationList, NotificationCounts

router = APIRouter(tags=["notifications"])

@router.get("/notifications", response_model=NotificationList)
async def get_user_notifications(
    unread_only: bool = Query(False, description="Only return unread notifications"),
    limit: int = Query(50, description="Maximum number of notifications to return"),
    offset: int = Query(0, description="Number of notifications to skip"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get notifications for the current user based on their role
    """
    return get_user_notifications_logic(db, str(current_user.id), unread_only, limit, offset)

@router.post("/{notification_id}/mark-read")
async def mark_notification_as_read(
    notification_id: str = Path(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a notification as read for the current user
    """
    notification_uuid = validate_notification_id(notification_id)
    return mark_notification_as_read_logic(db, notification_uuid, str(current_user.id))

@router.post("/{notification_id}/dismiss")
async def dismiss_notification(
    notification_id: str = Path(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Dismiss a notification for the current user
    """
    notification_uuid = validate_notification_id(notification_id)
    return dismiss_notification_logic(db, notification_uuid, str(current_user.id))

@router.post("/mark-all-read")
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark all notifications as read for the current user
    """
    return mark_all_notifications_as_read_logic(db, str(current_user.id))

@router.post("/create")
async def create_notification(
    request: CreateNotificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new notification for specified roles
    """
    return create_notification_logic(db, request, str(current_user.id))

@router.get("/count", response_model=NotificationCounts)
async def get_notification_counts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get notification counts by type and priority for the current user
    """
    return get_notification_counts_logic(db, str(current_user.id))