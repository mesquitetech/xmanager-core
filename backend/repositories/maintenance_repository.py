"""
Repository layer for Maintenance operations
Handles all database interactions for work orders and maintenance records
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from uuid import UUID
from datetime import datetime

from models import WorkOrder, MaintenanceRecord, Site, User, Equipment, WorkOrderStatus, Notification


def get_work_orders_from_db(db: Session, status: Optional[str] = None, site_id: Optional[UUID] = None) -> List[WorkOrder]:
    """Get work orders from database with optional filters"""
    try:
        query = db.query(WorkOrder)
        
        # Apply filters if provided
        if status:
            query = query.filter(WorkOrder.status == status)
        if site_id:
            query = query.filter(WorkOrder.site_id == site_id)
        
        return query.all()
        
    except Exception as e:
        print(f"Error getting work orders: {e}")
        return []


def get_work_order_by_id(db: Session, work_order_id: UUID) -> Optional[WorkOrder]:
    """Get work order by ID"""
    try:
        return db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    except Exception as e:
        print(f"Error getting work order: {e}")
        return None


def create_work_order_in_db(db: Session, work_order_data: Dict[str, Any]) -> Optional[WorkOrder]:
    """Create new work order in database"""
    try:
        new_work_order = WorkOrder(**work_order_data)
        db.add(new_work_order)
        db.commit()
        db.refresh(new_work_order)
        return new_work_order
        
    except Exception as e:
        db.rollback()
        print(f"Error creating work order: {e}")
        return None


def update_work_order_in_db(db: Session, work_order_id: UUID, work_order_data: Dict[str, Any]) -> Optional[WorkOrder]:
    """Update work order in database"""
    try:
        work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if not work_order:
            return None
            
        # Update fields
        for field, value in work_order_data.items():
            if hasattr(work_order, field) and value is not None:
                setattr(work_order, field, value)
        
        db.commit()
        db.refresh(work_order)
        return work_order
        
    except Exception as e:
        db.rollback()
        print(f"Error updating work order: {e}")
        return None


def delete_work_order_from_db(db: Session, work_order_id: UUID) -> bool:
    """Delete work order from database"""
    try:
        work_order = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if not work_order:
            return False
            
        db.delete(work_order)
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"Error deleting work order: {e}")
        return False


def get_site_by_id(db: Session, site_id: UUID) -> Optional[Site]:
    """Get site by ID"""
    try:
        return db.query(Site).filter(Site.id == site_id).first()
    except Exception as e:
        print(f"Error getting site: {e}")
        return None


def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
    """Get user by ID"""
    try:
        return db.query(User).filter(User.id == user_id).first()
    except Exception as e:
        print(f"Error getting user: {e}")
        return None


def get_maintenance_records_by_work_order(db: Session, work_order_id: UUID) -> List[MaintenanceRecord]:
    """Get maintenance records for a work order"""
    try:
        return db.query(MaintenanceRecord).filter(
            MaintenanceRecord.work_order_id == work_order_id
        ).all()
    except Exception as e:
        print(f"Error getting maintenance records: {e}")
        return []


def get_equipment_by_id(db: Session, equipment_id: UUID) -> Optional[Equipment]:
    """Get equipment by ID"""
    try:
        return db.query(Equipment).filter(Equipment.id == equipment_id).first()
    except Exception as e:
        print(f"Error getting equipment: {e}")
        return None


def create_notification_in_db(db: Session, notification_data: Dict[str, Any]) -> Optional[Notification]:
    """Create notification in database"""
    try:
        notification = Notification(**notification_data)
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification
        
    except Exception as e:
        db.rollback()
        print(f"Error creating notification: {e}")
        return None


def get_maintenance_records_from_db(db: Session, work_order_id: Optional[UUID] = None, equipment_id: Optional[UUID] = None) -> List[MaintenanceRecord]:
    """Get maintenance records with optional filters"""
    try:
        query = db.query(MaintenanceRecord)
        
        if work_order_id:
            query = query.filter(MaintenanceRecord.work_order_id == work_order_id)
        if equipment_id:
            query = query.filter(MaintenanceRecord.equipment_id == equipment_id)
        
        return query.all()
        
    except Exception as e:
        print(f"Error getting maintenance records: {e}")
        return []


def get_maintenance_record_by_id(db: Session, record_id: UUID) -> Optional[MaintenanceRecord]:
    """Get maintenance record by ID"""
    try:
        return db.query(MaintenanceRecord).filter(MaintenanceRecord.id == record_id).first()
    except Exception as e:
        print(f"Error getting maintenance record: {e}")
        return None


def create_maintenance_record_in_db(db: Session, record_data: Dict[str, Any]) -> Optional[MaintenanceRecord]:
    """Create new maintenance record in database"""
    try:
        new_record = MaintenanceRecord(**record_data)
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        return new_record
        
    except Exception as e:
        db.rollback()
        print(f"Error creating maintenance record: {e}")
        return None


def update_maintenance_record_in_db(db: Session, record_id: UUID, record_data: Dict[str, Any]) -> Optional[MaintenanceRecord]:
    """Update maintenance record in database"""
    try:
        record = db.query(MaintenanceRecord).filter(MaintenanceRecord.id == record_id).first()
        if not record:
            return None
            
        # Update fields
        for field, value in record_data.items():
            if hasattr(record, field) and value is not None:
                setattr(record, field, value)
        
        db.commit()
        db.refresh(record)
        return record
        
    except Exception as e:
        db.rollback()
        print(f"Error updating maintenance record: {e}")
        return None


def delete_maintenance_record_from_db(db: Session, record_id: UUID) -> bool:
    """Delete maintenance record from database"""
    try:
        record = db.query(MaintenanceRecord).filter(MaintenanceRecord.id == record_id).first()
        if not record:
            return False
            
        db.delete(record)
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"Error deleting maintenance record: {e}")
        return False


def get_work_orders_by_site(db: Session, site_id: UUID) -> List[WorkOrder]:
    """Get work orders by site ID"""
    try:
        return db.query(WorkOrder).filter(WorkOrder.site_id == site_id).all()
    except Exception as e:
        print(f"Error getting work orders by site: {e}")
        return []


def get_work_orders_by_status(db: Session, status: WorkOrderStatus) -> List[WorkOrder]:
    """Get work orders by status"""
    try:
        return db.query(WorkOrder).filter(WorkOrder.status == status).all()
    except Exception as e:
        print(f"Error getting work orders by status: {e}")
        return []


def get_work_orders_by_assigned_user(db: Session, user_id: UUID) -> List[WorkOrder]:
    """Get work orders assigned to a specific user"""
    try:
        return db.query(WorkOrder).filter(WorkOrder.assigned_to_id == user_id).all()
    except Exception as e:
        print(f"Error getting work orders by assigned user: {e}")
        return []


def count_work_orders(db: Session, status: Optional[str] = None, site_id: Optional[UUID] = None) -> int:
    """Count work orders with optional filters"""
    try:
        query = db.query(WorkOrder)
        
        if status:
            query = query.filter(WorkOrder.status == status)
        if site_id:
            query = query.filter(WorkOrder.site_id == site_id)
        
        return query.count()
        
    except Exception as e:
        print(f"Error counting work orders: {e}")
        return 0


def get_work_orders_with_pagination(db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None, site_id: Optional[UUID] = None) -> List[WorkOrder]:
    """Get work orders with pagination"""
    try:
        query = db.query(WorkOrder)
        
        if status:
            query = query.filter(WorkOrder.status == status)
        if site_id:
            query = query.filter(WorkOrder.site_id == site_id)
        
        return query.offset(skip).limit(limit).all()
        
    except Exception as e:
        print(f"Error getting work orders with pagination: {e}")
        return []