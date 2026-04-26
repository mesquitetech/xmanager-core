from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, UUID4
from models import WorkOrderStatus

# Pydantic models for WorkOrders
class WorkOrderBase(BaseModel):
    title: str
    description: Optional[str] = None
    work_type: str
    priority: str
    scheduled_start: datetime
    scheduled_end: Optional[datetime] = None
    checklist: Optional[Dict[str, bool]] = None
    materials_used: Optional[List[str]] = None
    attachments: Optional[List[str]] = None
    notes: Optional[str] = None

class WorkOrderCreate(WorkOrderBase):
    site_id: UUID4
    assigned_to_id: Optional[UUID4] = None
    incident_id: Optional[UUID4] = None

class WorkOrderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    work_type: Optional[str] = None
    status: Optional[WorkOrderStatus] = None
    priority: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    checklist: Optional[Dict[str, bool]] = None
    materials_used: Optional[List[str]] = None
    labor_hours: Optional[float] = None
    total_cost: Optional[float] = None
    attachments: Optional[List[str]] = None
    notes: Optional[str] = None
    assigned_to_id: Optional[UUID4] = None

class WorkOrderResponse(WorkOrderBase):
    id: UUID4
    site_id: UUID4
    site_name: Optional[str] = None
    incident_id: Optional[UUID4] = None
    access_log_id: Optional[UUID4] = None
    created_by_id: UUID4
    created_by_name: Optional[str] = None
    assigned_to_id: Optional[UUID4] = None
    assigned_to_name: Optional[str] = None
    status: WorkOrderStatus
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    labor_hours: Optional[float] = None
    total_cost: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    maintenance_records: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True

# Pydantic models for MaintenanceRecords
class MaintenanceRecordBase(BaseModel):
    maintenance_type: str
    description: str
    action_taken: str
    parts_replaced: Optional[List[str]] = None
    performed_at: datetime
    performed_by: str
    next_maintenance_date: Optional[datetime] = None
    attachments: Optional[List[str]] = None
    notes: Optional[str] = None

class MaintenanceRecordCreate(MaintenanceRecordBase):
    work_order_id: UUID4
    equipment_id: Optional[UUID4] = None

class MaintenanceRecordUpdate(BaseModel):
    maintenance_type: Optional[str] = None
    description: Optional[str] = None
    action_taken: Optional[str] = None
    parts_replaced: Optional[List[str]] = None
    performed_at: Optional[datetime] = None
    performed_by: Optional[str] = None
    next_maintenance_date: Optional[datetime] = None
    attachments: Optional[List[str]] = None
    notes: Optional[str] = None
    equipment_id: Optional[UUID4] = None

class MaintenanceRecordResponse(MaintenanceRecordBase):
    id: UUID4
    work_order_id: UUID4
    equipment_id: Optional[UUID4] = None
    equipment_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True