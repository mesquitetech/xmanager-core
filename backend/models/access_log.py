import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class AccessLog(Base):
    __tablename__ = "access_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    check_in_time = Column(DateTime)
    check_out_time = Column(DateTime, nullable=True)
    purpose = Column(String)
    activities = Column(Text)
    photos = Column(JSONB)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    site = relationship("Site", back_populates="access_logs")
    user = relationship("User", back_populates="access_logs")
    work_orders = relationship("WorkOrder", back_populates="access_log")