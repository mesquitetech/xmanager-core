import uuid
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class OperationalExpense(Base):
    __tablename__ = "operational_expenses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"))
    name = Column(String, nullable=False)  # Nombre del gasto
    category = Column(String, nullable=False)  # utilities, maintenance, rent, etc.
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    expense_date = Column(DateTime, nullable=False)
    description = Column(Text)
    notes = Column(Text)  # Notas adicionales
    vendor = Column(String)
    invoice_number = Column(String)
    payment_status = Column(String, default="pending")
    payment_method = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    site = relationship("Site", back_populates="operational_expenses")