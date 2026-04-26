import uuid
from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.database import Base

class SiteNetworkInfo(Base):
    __tablename__ = "site_network_info"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), unique=True)
    ip_address = Column(String)
    subnet_mask = Column(String)
    gateway = Column(String)
    dns_primary = Column(String)
    dns_secondary = Column(String)
    bandwidth_upload = Column(Float)
    bandwidth_download = Column(Float)
    network_provider = Column(String)
    circuit_id = Column(String)

    # Relationships
    site = relationship("Site", back_populates="network_info")