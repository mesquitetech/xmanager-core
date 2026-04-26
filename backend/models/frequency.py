from sqlalchemy import Column, String, Date, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from db.database import Base
import uuid

class SiteFrequencyInventory(Base):
    __tablename__ = "site_frequency_inventory"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)
    plaza = Column(String(200))
    ip_gestion = Column(String(50))
    dispositivo = Column(String(200))
    frecuencia_1 = Column(String(20))
    frecuencia_2 = Column(String(20))
    banda = Column(String(50))
    ssid = Column(String(200))
    estado = Column(String(50), default="Activa")
    fecha_instalacion = Column(Date)
    fecha_retiro = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship with Site
    site = relationship("Site", back_populates="frequency_inventory")