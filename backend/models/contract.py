import uuid
from sqlalchemy import Column, String, DateTime, Text, Float, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class Contract(Base):
    __tablename__ = "contracts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String)
    type = Column(String)  # Matches database column name
    related_party = Column(String)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    value = Column(Float)
    status = Column(String, default="active")
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(UUID(as_uuid=True))
    updated_by_id = Column(UUID(as_uuid=True))
    party_phone = Column(String)
    party_email = Column(String)
    contract_date = Column(DateTime)
    rent_amount = Column(Float)
    requires_invoice = Column(Boolean, default=False)
    is_courtesy_service = Column(Boolean, default=False)
    courtesy_service_type = Column(String)
    party_contact_name = Column(String)

    # Relationships
    site = relationship("Site")
    documents = relationship("ContractDocument", back_populates="contract", cascade="all, delete-orphan")