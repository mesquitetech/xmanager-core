"""
Service layer for Notification operations
Handles business logic and validation for notifications
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from uuid import UUID
from datetime import datetime, timedelta

from repositories.notification_repository import (
    get_notifications_from_db,
    get_notification_by_id,
    create_notification_in_db,
    update_notification_in_db,
    delete_notification_from_db,
    get_user_notification,
    create_or_update_user_notification,
    get_unread_count,
    get_all_notifications_for_user,
    get_user_role_from_db,
    get_notification_counts_by_type_and_priority
)
from api.notifications.schemas import (
    NotificationCreate, NotificationUpdate, NotificationResponse, 
    UserNotificationUpdate, NotificationList, CreateNotificationRequest,
    NotificationCounts
)
from models import NotificationTypeEnum, NotificationPriorityEnum, Site, SiteLegalInfo


def get_user_notifications_logic(
    db: Session, 
    user_id: UUID,
    unread_only: bool = False, 
    limit: int = 50, 
    offset: int = 0
) -> NotificationList:
    """Get notifications for a user with business logic validation"""
    try:
        # Get user role
        user_role = get_user_role_from_db(db, user_id) or "operativo"
        
        # Get notifications with read status
        results = get_notifications_from_db(db, user_id, user_role, unread_only, limit, offset)
        
        # Format response
        notifications = []
        for notification, is_read, read_at, is_dismissed in results:
            notification_data = NotificationResponse(
                id=notification.id,
                title=notification.title,
                message=notification.message,
                notification_type=notification.notification_type,
                priority=notification.priority,
                target_role=notification.target_role,
                related_id=notification.related_id,
                related_table=notification.related_table,
                expires_at=notification.expires_at,
                meta_data=notification.meta_data,
                created_by_id=notification.created_by_id,
                created_at=notification.created_at,
                is_system_generated=notification.is_system_generated,
                is_read=is_read if is_read is not None else False,
                read_at=read_at,
                is_dismissed=is_dismissed if is_dismissed is not None else False
            )
            notifications.append(notification_data)
        
        # Get unread count
        unread_count = get_unread_count(db, user_id, user_role)
        
        return NotificationList(
            notifications=notifications,
            unread_count=unread_count,
            total_returned=len(notifications)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching notifications: {str(e)}"
        )


def mark_notification_as_read_logic(db: Session, notification_id: UUID, user_id: UUID) -> Dict[str, str]:
    """Mark a notification as read for a user"""
    # Validate notification exists
    notification = get_notification_by_id(db, notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    try:
        # Update user notification
        update_data = UserNotificationUpdate(is_read=True)
        create_or_update_user_notification(db, notification_id, user_id, update_data)
        
        return {"message": "Notification marked as read"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error marking notification as read: {str(e)}"
        )


def dismiss_notification_logic(db: Session, notification_id: UUID, user_id: UUID) -> Dict[str, str]:
    """Dismiss a notification for a user"""
    # Validate notification exists
    notification = get_notification_by_id(db, notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    try:
        # Update user notification
        update_data = UserNotificationUpdate(is_dismissed=True)
        create_or_update_user_notification(db, notification_id, user_id, update_data)
        
        return {"message": "Notification dismissed"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error dismissing notification: {str(e)}"
        )


def mark_all_notifications_as_read_logic(db: Session, user_id: UUID) -> Dict[str, str]:
    """Mark all notifications as read for a user"""
    try:
        # Get user role
        user_role = get_user_role_from_db(db, user_id) or "operativo"
        
        # Get all notifications for the user
        notifications = get_all_notifications_for_user(db, user_id, user_role)
        
        # Mark each as read
        for notification in notifications:
            user_notification = get_user_notification(db, notification.id, user_id)
            
            if not user_notification or not user_notification.is_read:
                update_data = UserNotificationUpdate(is_read=True)
                create_or_update_user_notification(db, notification.id, user_id, update_data)
        
        return {"message": "All notifications marked as read"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error marking all notifications as read: {str(e)}"
        )


def create_notification_logic(db: Session, request: CreateNotificationRequest, user_id: UUID) -> Dict[str, Any]:
    """Create a new notification"""
    try:
        # Create notification data
        notification_data = NotificationCreate(
            title=request.title,
            message=request.message,
            notification_type=request.notification_type,
            priority=request.priority,
            target_role=request.target_roles[0] if request.target_roles else "operativo",
            expires_at=request.expires_at,
            related_id=request.related_id,
            related_table=request.related_table,
            meta_data=request.meta_data
        )
        
        # Create notification
        notification = create_notification_in_db(db, notification_data, user_id)
        
        return {
            "message": "Notification created successfully",
            "notification_id": str(notification.id)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating notification: {str(e)}"
        )


def get_notification_counts_logic(db: Session, user_id: UUID) -> NotificationCounts:
    """Get notification counts by type and priority"""
    try:
        # Get user role
        user_role = get_user_role_from_db(db, user_id) or "operativo"
        
        # Get base counts
        counts_data = get_notification_counts_by_type_and_priority(db, user_id, user_role)
        
        # Get counts by priority and type using simple filters
        priority_counts = {"low": 0, "normal": 0, "high": 0, "critical": 0}
        type_counts = {"info": 0, "warning": 0, "error": 0, "success": 0}
        
        # For now, return basic counts - can be enhanced later with specific queries
        return NotificationCounts(
            total=counts_data["total"],
            unread=counts_data["unread"],
            by_priority=priority_counts,
            by_type=type_counts
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting notification counts: {str(e)}"
        )


def validate_notification_id(notification_id: str) -> UUID:
    """Validate and convert notification ID to UUID"""
    try:
        return UUID(notification_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid notification ID format"
        )

# ============================================================================
# SPECIALIZED DOMAIN NOTIFICATION CREATORS (migrated from old services.py)
# ============================================================================

def create_site_notification(
    db: Session,
    action: str,  # "created", "updated", "deleted"
    site_name: str,
    site_id: UUID,
    created_by_id: Optional[UUID] = None
):
    """Create notifications for site changes (operativo, juridico, financiero)"""
    if action == "created":
        title = "Nueva Torre Agregada"
        message = f"Se ha agregado una nueva torre: {site_name}"
        priority = "normal"
    elif action == "deleted":
        title = "Torre Eliminada"
        message = f"Se ha eliminado la torre: {site_name}"
        priority = "high"
    else:  # updated
        title = "Torre Actualizada"
        message = f"Se ha actualizado la torre: {site_name}"
        priority = "normal"
    
    # Create notifications for each target role
    for role in ["operativo", "juridico", "financiero"]:
        notification_data = NotificationCreate(
            title=title,
            message=message,
            notification_type="site",
            priority=priority,
            target_role=role,
            related_id=site_id,
            related_table="sites",
            meta_data={"action": action, "site_name": site_name}
        )
        create_notification_in_db(db, notification_data, created_by_id)

def create_maintenance_notification(
    db: Session,
    action: str,  # "assigned", "status_changed", "created"
    maintenance_id: UUID,
    site_name: str,
    status: Optional[str] = None,
    assigned_to_id: Optional[UUID] = None,
    created_by_id: Optional[UUID] = None
):
    """Create notifications for maintenance orders (operativo)"""
    if action == "assigned":
        title = "Orden de Mantenimiento Asignada"
        message = f"Se le ha asignado una orden de mantenimiento para el sitio: {site_name}"
        priority = "high"
    elif action == "status_changed":
        title = "Cambio de Status en Orden de Mantenimiento"
        message = f"La orden de mantenimiento del sitio {site_name} ha cambiado a: {status}"
        priority = "normal"
    else:  # created
        title = "Nueva Orden de Mantenimiento"
        message = f"Se ha creado una nueva orden de mantenimiento para: {site_name}"
        priority = "normal"
    
    notification_data = NotificationCreate(
        title=title,
        message=message,
        notification_type="maintenance",
        priority=priority,
        target_role="operativo",
        related_id=maintenance_id,
        related_table="maintenance_orders",
        meta_data={
            "action": action, 
            "site_name": site_name, 
            "status": status,
            "assigned_to_id": str(assigned_to_id) if assigned_to_id else None
        }
    )
    create_notification_in_db(db, notification_data, created_by_id)

def create_payment_notification(
    db: Session,
    action: str,  # "pending", "overdue", "paid"
    site_name: str,
    site_id: UUID,
    amount: Optional[float] = None,
    due_date: Optional[datetime] = None,
    created_by_id: Optional[UUID] = None
):
    """Create notifications for payments (financiero)"""
    if action == "pending":
        title = "Pago Pendiente"
        message = f"Pago pendiente para el sitio: {site_name}"
        if amount:
            message += f" por ${amount:,.2f}"
        if due_date:
            message += f". Vence el {due_date.strftime('%d/%m/%Y')}"
        priority = "normal"
    elif action == "overdue":
        title = "Pago Vencido"
        message = f"PAGO VENCIDO para el sitio: {site_name}"
        if amount:
            message += f" por ${amount:,.2f}"
        priority = "critical"
    else:  # paid
        title = "Pago Realizado"
        message = f"Se ha registrado el pago para el sitio: {site_name}"
        if amount:
            message += f" por ${amount:,.2f}"
        priority = "low"
    
    notification_data = NotificationCreate(
        title=title,
        message=message,
        notification_type="payment",
        priority=priority,
        target_role="financiero",
        related_id=site_id,
        related_table="sites",
        meta_data={
            "action": action, 
            "site_name": site_name, 
            "amount": amount,
            "due_date": due_date.isoformat() if due_date else None
        }
    )
    create_notification_in_db(db, notification_data, created_by_id)