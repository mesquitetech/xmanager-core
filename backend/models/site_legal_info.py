import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.database import Base
from sqlalchemy.sql import func
class SiteLegalInfo(Base):
    __tablename__ = "site_legal_info"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), unique=True)
    contract_start_date = Column(DateTime)
    contract_end_date = Column(DateTime)
    contract_document_path = Column(String)
    monthly_rent = Column(Float)
    currency = Column(String, default="USD")
    landlord_name = Column(String)
    landlord_contact = Column(String)
    landlord_email = Column(String)
    payment_frequency = Column(String, default="monthly")
    next_payment_date = Column(DateTime)
    payment_status = Column(String, default="unpaid")
    payment_evidence_file = Column(String)
    payment_evidence_type = Column(String)
    service_provider = Column(String)
    service_provider_contact = Column(String)
    service_provider_email = Column(String)
    
    # Additional fields that exist in database
    electricity_support = Column(String)
    internet_exchange = Column(String)
    period = Column(String)
    noc_status = Column(String)
    infra_status = Column(String)
    network_arch_status = Column(String)
    classification = Column(String)
    contract_date = Column(DateTime)
    requires_invoice = Column(String)
    courtesy_service = Column(String)
    courtesy_service_details = Column(Text)
    landlord_phone = Column(String)
    notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    site = relationship("Site", back_populates="legal_info")