"""
Repository layer for Notification operations
Handles all database interactions for notifications and user notifications
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
from datetime import datetime
from uuid import UUID

from models import Notification, UserNotification, User
from api.notifications.schemas import NotificationCreate, NotificationUpdate, UserNotificationUpdate


def get_notifications_from_db(
    db: Session, 
    user_id: UUID, 
    user_role: str,
    unread_only: bool = False, 
    limit: int = 50, 
    offset: int = 0
) -> List[Tuple]:
    """Get notifications for a user with their read status"""
    query = db.query(
        Notification,
        UserNotification.is_read,
        UserNotification.read_at,
        UserNotification.is_dismissed
    ).outerjoin(
        UserNotification,
        and_(
            UserNotification.notification_id == Notification.id,
            UserNotification.user_id == user_id
        )
    ).filter(
        or_(
            Notification.target_role == user_role,
            Notification.target_role == "administrador"
        )
    )
    
    # Filter out expired notifications
    query = query.filter(
        or_(
            Notification.expires_at.is_(None),
            Notification.expires_at > datetime.utcnow()
        )
    )
    
    # If unread_only is True, filter to only unread notifications
    if unread_only:
        query = query.filter(
            or_(
                UserNotification.is_read.is_(None),
                UserNotification.is_read == False
            )
        )
    
    # Order by priority and creation date
    query = query.order_by(
        desc(Notification.priority),
        desc(Notification.created_at)
    )
    
    return query.offset(offset).limit(limit).all()


def get_notification_by_id(db: Session, notification_id: UUID) -> Optional[Notification]:
    """Get a single notification by ID"""
    return db.query(Notification).filter(Notification.id == notification_id).first()


def create_notification_in_db(db: Session, notification_data: NotificationCreate, created_by_id: UUID) -> Notification:
    """Create a new notification in database"""
    db_notification = Notification(
        title=notification_data.title,
        message=notification_data.message,
        notification_type=notification_data.notification_type,
        priority=notification_data.priority,
        target_role=notification_data.target_role,
        related_id=notification_data.related_id,
        related_table=notification_data.related_table,
        expires_at=notification_data.expires_at,
        meta_data=notification_data.meta_data,
        created_by_id=created_by_id,
        is_system_generated=False
    )
    
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


def update_notification_in_db(db: Session, notification_id: UUID, notification_data: NotificationUpdate) -> Optional[Notification]:
    """Update an existing notification"""
    notification = get_notification_by_id(db, notification_id)
    if not notification:
        return None
    
    update_data = notification_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(notification, field, value)
    
    db.commit()
    db.refresh(notification)
    return notification


def delete_notification_from_db(db: Session, notification_id: UUID) -> bool:
    """Delete a notification from database"""
    notification = get_notification_by_id(db, notification_id)
    if not notification:
        return False
    
    db.delete(notification)
    db.commit()
    return True


def get_user_notification(db: Session, notification_id: UUID, user_id: UUID) -> Optional[UserNotification]:
    """Get user notification record"""
    return db.query(UserNotification).filter(
        and_(
            UserNotification.notification_id == notification_id,
            UserNotification.user_id == user_id
        )
    ).first()


def create_or_update_user_notification(
    db: Session, 
    notification_id: UUID, 
    user_id: UUID, 
    update_data: UserNotificationUpdate
) -> UserNotification:
    """Create or update user notification record"""
    user_notification = get_user_notification(db, notification_id, user_id)
    
    if not user_notification:
        # Create new record
        user_notification = UserNotification(
            notification_id=notification_id,
            user_id=user_id,
            is_read=update_data.is_read if update_data.is_read is not None else False,
            is_dismissed=update_data.is_dismissed if update_data.is_dismissed is not None else False
        )
        
        if update_data.is_read:
            user_notification.read_at = datetime.utcnow()
        if update_data.is_dismissed:
            user_notification.dismissed_at = datetime.utcnow()
            
        db.add(user_notification)
    else:
        # Update existing record
        if update_data.is_read is not None:
            user_notification.is_read = update_data.is_read
            if update_data.is_read:
                user_notification.read_at = datetime.utcnow()
        
        if update_data.is_dismissed is not None:
            user_notification.is_dismissed = update_data.is_dismissed
            if update_data.is_dismissed:
                user_notification.dismissed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(user_notification)
    return user_notification


def get_unread_count(db: Session, user_id: UUID, user_role: str) -> int:
    """Get count of unread notifications for a user"""
    return db.query(func.count(Notification.id)).outerjoin(
        UserNotification,
        and_(
            UserNotification.notification_id == Notification.id,
            UserNotification.user_id == user_id
        )
    ).filter(
        or_(
            Notification.target_role == user_role,
            Notification.target_role == "administrador"
        ),
        or_(
            Notification.expires_at.is_(None),
            Notification.expires_at > datetime.utcnow()
        ),
        or_(
            UserNotification.is_read.is_(None),
            UserNotification.is_read == False
        )
    ).scalar()


def get_all_notifications_for_user(db: Session, user_id: UUID, user_role: str) -> List[Notification]:
    """Get all non-expired notifications for a user role"""
    return db.query(Notification).filter(
        or_(
            Notification.target_role == user_role,
            Notification.target_role == "administrador"
        ),
        or_(
            Notification.expires_at.is_(None),
            Notification.expires_at > datetime.utcnow()
        )
    ).all()


def get_user_role_from_db(db: Session, user_id: UUID) -> Optional[str]:
    """Get user role name by user ID"""
    result = db.execute(
        text("SELECT r.name FROM users u JOIN roles r ON u.role_id = r.id WHERE u.id = :user_id"),
        {"user_id": str(user_id)}
    ).fetchone()
    return result[0] if result else None


def get_notification_counts_by_type_and_priority(db: Session, user_id: UUID, user_role: str) -> Dict[str, Any]:
    """Get detailed notification counts by type and priority"""
    base_query = db.query(Notification).outerjoin(
        UserNotification,
        and_(
            UserNotification.notification_id == Notification.id,
            UserNotification.user_id == user_id
        )
    ).filter(
        or_(
            Notification.target_role == user_role,
            Notification.target_role == "administrador"
        ),
        or_(
            UserNotification.is_dismissed.is_(None),
            UserNotification.is_dismissed.is_(False)
        ),
        or_(
            Notification.expires_at.is_(None),
            Notification.expires_at > datetime.utcnow()
        )
    )
    
    # Total count
    total = base_query.count()
    
    # Unread count
    unread = base_query.filter(
        or_(
            UserNotification.is_read.is_(None),
            UserNotification.is_read.is_(False)
        )
    ).count()
    
    return {
        "total": total,
        "unread": unread,
        "base_query": base_query
    }