import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class ContractDocument(Base):
    __tablename__ = "contract_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id = Column(UUID(as_uuid=True), ForeignKey("contracts.id"))
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    document_type = Column(String)  # contract, amendment, addendum, etc.
    version = Column(String, default="1.0")
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by = Column(String)

    # Relationships
    contract = relationship("Contract", back_populates="documents")