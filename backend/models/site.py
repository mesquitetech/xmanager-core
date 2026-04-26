import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from db.database import Base

class Site(Base):
    __tablename__ = "sites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, index=True)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    zip_code = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    geom = Column(Geometry(geometry_type='POINT', srid=4326))
    site_type = Column(String)
    status = Column(String)
    description = Column(Text)
    contact_name = Column(String)
    contact_phone = Column(String)
    contact_email = Column(String)
    # Campos adicionales personalizados
    rb_type = Column(String)  # Tipo de RB
    height = Column(Float)    # Altura (en metros)
    area_type = Column(String)  # Tipo de Área
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    legal_info = relationship("SiteLegalInfo", back_populates="site", uselist=False, cascade="all, delete-orphan")
    network_info = relationship("SiteNetworkInfo", back_populates="site", uselist=False, cascade="all, delete-orphan")
    energy_info = relationship("SiteEnergyInfo", back_populates="site", uselist=False, cascade="all, delete-orphan")
    infrastructure_info = relationship("SiteInfrastructureInfo", back_populates="site", uselist=False, cascade="all, delete-orphan")
    equipment = relationship("Equipment", secondary="site_equipment", back_populates="sites")
    payments = relationship("SitePayment", back_populates="site", cascade="all, delete-orphan")
    access_logs = relationship("AccessLog", back_populates="site", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="site", cascade="all, delete-orphan")
    work_orders = relationship("WorkOrder", back_populates="site", cascade="all, delete-orphan")
    photos = relationship("SitePhoto", back_populates="site", cascade="all, delete-orphan")
    payment_evidences = relationship("PaymentEvidence", back_populates="site", cascade="all, delete-orphan")
    operational_expenses = relationship("OperationalExpense", back_populates="site", cascade="all, delete-orphan")
    frequency_inventory = relationship("SiteFrequencyInventory", back_populates="site", cascade="all, delete-orphan")
    seguros = relationship("Seguro", back_populates="site", cascade="all, delete-orphan")