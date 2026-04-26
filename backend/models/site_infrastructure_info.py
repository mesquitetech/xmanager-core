import uuid
from sqlalchemy import Column, String, Float, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.database import Base

class SiteInfrastructureInfo(Base):
    __tablename__ = "site_infrastructure_info"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), unique=True)
    tower_height = Column(Float)
    tower_type = Column(String)
    foundation_type = Column(String)
    access_road = Column(Boolean, default=True)
    security_fence = Column(Boolean, default=False)
    building_area = Column(Float)
    shelter_type = Column(String)
    cooling_system = Column(String)

    # Relationships
    site = relationship("Site", back_populates="infrastructure_info")