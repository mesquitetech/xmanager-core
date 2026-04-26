import uuid
import enum
from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class IncidentPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"))
    reporter_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    assignee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)  # electrical, network, physical, security
    priority = Column(Enum(IncidentPriority), default=IncidentPriority.MEDIUM)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.OPEN)
    reported_at = Column(DateTime, default=func.now())
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text)
    attachments = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    site = relationship("Site", back_populates="incidents")
    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="incidents_reported")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="incidents_assigned")
    work_orders = relationship("WorkOrder", back_populates="incident")