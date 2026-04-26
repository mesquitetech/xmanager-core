import uuid
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class ExpenseEvidence(Base):
    __tablename__ = "expense_evidences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    expense_id = Column(UUID(as_uuid=True), ForeignKey("operational_expenses.id"))
    file_name = Column(String, nullable=False)
    file_type = Column(String)
    file_url = Column(String(500), nullable=True)       # URL en Supabase Storage
    file_data = Column(Text, nullable=True)             # Legacy: Base64 (registros antiguos)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relationships
    expense = relationship("OperationalExpense")