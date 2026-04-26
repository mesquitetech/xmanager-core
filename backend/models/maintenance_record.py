import uuid
from sqlalchemy import Column, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"))
    equipment_id = Column(UUID(as_uuid=True), ForeignKey("equipment.id"))
    maintenance_date = Column(DateTime, nullable=False)
    maintenance_type = Column(String)  # preventive, corrective, emergency
    description = Column(Text)
    technician = Column(String)
    parts_used = Column(Text)
    cost = Column(Float)
    status = Column(String, default="completed")
    next_maintenance_date = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    site = relationship("Site")
    equipment = relationship("Equipment")