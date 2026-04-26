from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from auth.utils import get_current_user
from db.database import get_db
from models import User
from services.maintenance_service import (
    get_work_orders_logic,
    get_work_order_by_id_logic,
    create_work_order_logic,
    update_work_order_logic,
    delete_work_order_logic,
    get_maintenance_records_logic,
    create_maintenance_record_logic
)
from .schemas import (
    WorkOrderCreate, WorkOrderResponse, WorkOrderUpdate,
    MaintenanceRecordCreate, MaintenanceRecordResponse, MaintenanceRecordUpdate
)

router = APIRouter()
# ruta para obtener todas las ordenes de trabajo
@router.get("/work-orders")
async def get_work_orders(
    status: Optional[str] = None,
    site_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener la lista de órdenes de trabajo con filtros opcionales
    """
    return get_work_orders_logic(db, status, site_id)

@router.post("/work-orders")
async def create_work_order(
    work_order_data: WorkOrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crear una nueva orden de trabajo
    """
    return create_work_order_logic(db, work_order_data, current_user.id)

@router.get("/work-orders/{work_order_id}")
async def get_work_order(
    work_order_id: UUID = Path(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener una orden de trabajo por ID
    """
    return get_work_order_by_id_logic(db, work_order_id)

@router.put("/work-orders/{work_order_id}")
async def update_work_order(
    work_order_data: WorkOrderUpdate,
    work_order_id: UUID = Path(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar una orden de trabajo existente
    """
    return update_work_order_logic(db, work_order_id, work_order_data)

@router.delete("/work-orders/{work_order_id}")
async def delete_work_order(
    work_order_id: UUID = Path(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar una orden de trabajo
    """
    return delete_work_order_logic(db, work_order_id)

@router.get("/records")
async def get_maintenance_records(
    work_order_id: Optional[UUID] = Query(None),
    equipment_id: Optional[UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener registros de mantenimiento con filtros opcionales
    """
    return get_maintenance_records_logic(db, work_order_id, equipment_id)

@router.post("/records")
async def create_maintenance_record(
    record_data: MaintenanceRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo registro de mantenimiento
    """
    return create_maintenance_record_logic(db, record_data)