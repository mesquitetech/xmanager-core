import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base

# Models
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_google_auth = Column(Boolean, default=False)
    is_firebase_auth = Column(Boolean, default=False)
    firebase_uid = Column(String, nullable=True, unique=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Nota: last_login está comentado porque no existe en la base de datos actual
    # Si se necesita, se debe agregar mediante una migración
    # last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    role = relationship("Role", back_populates="users")
    access_logs = relationship("AccessLog", back_populates="user")
    incidents_reported = relationship("Incident", foreign_keys="Incident.reporter_id", back_populates="reporter")
    incidents_assigned = relationship("Incident", foreign_keys="Incident.assignee_id", back_populates="assignee")
    work_orders_created = relationship("WorkOrder", foreign_keys="WorkOrder.created_by_id", back_populates="created_by")
    work_orders_assigned = relationship("WorkOrder", foreign_keys="WorkOrder.assigned_to_id", back_populates="assigned_to")
    preferences = relationship("UserPreference", back_populates="user", cascade="all, delete-orphan")