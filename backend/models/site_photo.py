import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class SitePhoto(Base):
    __tablename__ = "site_photos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"))
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    caption = Column(String)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by = Column(String)
    file_size = Column(String)
    file_type = Column(String)

    # Relationships
    site = relationship("Site", back_populates="photos")