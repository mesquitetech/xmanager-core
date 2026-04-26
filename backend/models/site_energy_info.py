import uuid
from sqlalchemy import Column, String, Float, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.database import Base

class SiteEnergyInfo(Base):
    __tablename__ = "site_energy_info"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), unique=True)
    power_source = Column(String)
    backup_power = Column(Boolean, default=False)
    generator_capacity = Column(Float)
    ups_capacity = Column(Float)
    monthly_power_consumption = Column(Float)
    power_provider = Column(String)
    meter_number = Column(String)
    average_monthly_cost = Column(Float)

    # Relationships
    site = relationship("Site", back_populates="energy_info")