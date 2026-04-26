import uuid
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    model = Column(String)
    serial_number = Column(String, unique=True)
    manufacturer = Column(String)
    category = Column(String)
    status = Column(String, default="active")
    installation_date = Column(DateTime)
    warranty_expiry = Column(DateTime)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Many-to-many relationship with sites
    sites = relationship("Site", secondary="site_equipment", back_populates="equipment")