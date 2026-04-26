"""
Service layer for Maintenance operations
Business logic for work orders and maintenance records
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID

from repositories.maintenance_repository import (
    get_work_orders_from_db,
    get_work_order_by_id,
    get_site_by_id,
    get_user_by_id
)


def get_work_orders_logic(db: Session, status: Optional[str] = None, site_id: Optional[UUID] = None) -> List[Dict[str, Any]]:
    """Business logic for getting work orders with filters"""
    
    try:
        # Get work orders from repository
        work_orders = get_work_orders_from_db(db, status, site_id)
        
        # Build response with additional information
        result = []
        for order in work_orders:
            # Get related information using repository
            site = get_site_by_id(db, order.site_id) if order.site_id else None
            created_by = get_user_by_id(db, order.created_by_id) if order.created_by_id else None
            assigned_to = get_user_by_id(db, order.assigned_to_id) if order.assigned_to_id else None
            
            work_order_dict = {
                "id": str(order.id),
                "title": order.title,
                "description": order.description,
                "work_type": order.work_type,
                "status": order.status.value if hasattr(order.status, 'value') else str(order.status),
                "priority": order.priority,
                "site_id": str(order.site_id) if order.site_id else None,
                "site_name": site.name if site else None,
                "created_by_id": str(order.created_by_id) if order.created_by_id else None,
                "created_by_name": f"{created_by.first_name} {created_by.last_name}" if created_by else None,
                "assigned_to_id": str(order.assigned_to_id) if order.assigned_to_id else None,
                "assigned_to_name": f"{assigned_to.first_name} {assigned_to.last_name}" if assigned_to else None,
                "scheduled_start": order.scheduled_start.isoformat() if order.scheduled_start else None,
                "scheduled_end": order.scheduled_end.isoformat() if order.scheduled_end else None,
                "actual_start": order.actual_start.isoformat() if order.actual_start else None,
                "actual_end": order.actual_end.isoformat() if order.actual_end else None,
                "labor_hours": order.labor_hours,
                "total_cost": order.total_cost,
                "notes": order.notes,
                "created_at": order.created_at.isoformat() if order.created_at else None,
                "updated_at": order.updated_at.isoformat() if order.updated_at else None
            }
            result.append(work_order_dict)
        
        return result
        
    except Exception as e:
        print(f"Error in get_work_orders_logic: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener órdenes de trabajo"
        )


def get_work_order_by_id_logic(db: Session, work_order_id: UUID) -> Dict[str, Any]:
    """Business logic for getting work order by ID"""
    
    try:
        # Get work order from repository
        work_order = get_work_order_by_id(db, work_order_id)
        if not work_order:
            raise HTTPException(
                status_code=404,
                detail="Orden de trabajo no encontrada"
            )
        
        # Get related information using repository
        site = get_site_by_id(db, work_order.site_id) if work_order.site_id else None
        created_by = get_user_by_id(db, work_order.created_by_id) if work_order.created_by_id else None
        assigned_to = get_user_by_id(db, work_order.assigned_to_id) if work_order.assigned_to_id else None
        
        return {
            "id": str(work_order.id),
            "title": work_order.title,
            "description": work_order.description,
            "work_type": work_order.work_type,
            "status": work_order.status.value if hasattr(work_order.status, 'value') else str(work_order.status),
            "priority": work_order.priority,
            "site_id": str(work_order.site_id) if work_order.site_id else None,
            "site_name": site.name if site else None,
            "created_by_id": str(work_order.created_by_id) if work_order.created_by_id else None,
            "created_by_name": f"{created_by.first_name} {created_by.last_name}" if created_by else None,
            "assigned_to_id": str(work_order.assigned_to_id) if work_order.assigned_to_id else None,
            "assigned_to_name": f"{assigned_to.first_name} {assigned_to.last_name}" if assigned_to else None,
            "scheduled_start": work_order.scheduled_start.isoformat() if work_order.scheduled_start else None,
            "scheduled_end": work_order.scheduled_end.isoformat() if work_order.scheduled_end else None,
            "actual_start": work_order.actual_start.isoformat() if work_order.actual_start else None,
            "actual_end": work_order.actual_end.isoformat() if work_order.actual_end else None,
            "labor_hours": work_order.labor_hours,
            "total_cost": work_order.total_cost,
            "notes": work_order.notes,
            "created_at": work_order.created_at.isoformat() if work_order.created_at else None,
            "updated_at": work_order.updated_at.isoformat() if work_order.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_work_order_by_id_logic: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener orden de trabajo"
        )


# Placeholder functions for compatibility
def create_work_order_logic(db: Session, work_order_data, created_by_id: UUID):
    """Placeholder for create work order"""
    raise HTTPException(status_code=501, detail="Funcionalidad no implementada")

def update_work_order_logic(db: Session, work_order_id: UUID, work_order_data):
    """Placeholder for update work order"""
    raise HTTPException(status_code=501, detail="Funcionalidad no implementada")

def delete_work_order_logic(db: Session, work_order_id: UUID):
    """Placeholder for delete work order"""
    raise HTTPException(status_code=501, detail="Funcionalidad no implementada")

def get_maintenance_records_logic(db: Session, work_order_id: Optional[UUID] = None):
    """Placeholder for maintenance records"""
    return []

def create_maintenance_record_logic(db: Session, record_data, created_by_id: UUID):
    """Placeholder for create maintenance record"""
    raise HTTPException(status_code=501, detail="Funcionalidad no implementada")