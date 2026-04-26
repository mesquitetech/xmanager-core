import uuid
import enum
from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class WorkOrderStatus(str, enum.Enum):
    DRAFT = "draft"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"))
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=True)
    access_log_id = Column(UUID(as_uuid=True), ForeignKey("access_logs.id"), nullable=True)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    work_type = Column(String)  # preventive, corrective, installation
    status = Column(Enum(WorkOrderStatus), default=WorkOrderStatus.DRAFT)
    priority = Column(String)
    scheduled_start = Column(DateTime)
    scheduled_end = Column(DateTime)
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)
    materials_needed = Column(JSONB)
    materials_used = Column(JSONB)
    labor_hours = Column(String)
    cost_estimate = Column(String)
    actual_cost = Column(String)
    completion_notes = Column(Text)
    attachments = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    site = relationship("Site", back_populates="work_orders")
    incident = relationship("Incident", back_populates="work_orders")
    access_log = relationship("AccessLog", back_populates="work_orders")
    created_by = relationship("User", foreign_keys=[created_by_id], back_populates="work_orders_created")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], back_populates="work_orders_assigned")