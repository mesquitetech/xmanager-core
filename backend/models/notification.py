import uuid
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String, default="info")
    priority = Column(String, default="normal")
    target_role = Column(String, nullable=True)
    related_id = Column(UUID(as_uuid=True), nullable=True)
    related_table = Column(String, nullable=True)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_system_generated = Column(Boolean, default=False)
    meta_data = Column(JSONB, nullable=True)

    # Relationships
    user_notifications = relationship("UserNotification", back_populates="notification")
    created_by = relationship("User", foreign_keys=[created_by_id])