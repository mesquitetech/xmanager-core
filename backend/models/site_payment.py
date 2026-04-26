import uuid
from sqlalchemy import Column, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class SitePayment(Base):
    __tablename__ = "site_payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"))
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    payment_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime)
    payment_type = Column(String)  # rent, utilities, maintenance, etc.
    status = Column(String, default="pending")  # pending, paid, overdue
    payment_method = Column(String)
    reference_number = Column(String)
    notes = Column(String)
    is_recurring = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    site = relationship("Site", back_populates="payments")