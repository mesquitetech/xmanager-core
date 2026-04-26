import uuid
from sqlalchemy import Column, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.database import Base

class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"))
    module_id = Column(UUID(as_uuid=True), ForeignKey("modules.id"))
    can_create = Column(Boolean, default=False)
    can_read = Column(Boolean, default=False)
    can_update = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    can_approve = Column(Boolean, default=False)
    can_export = Column(Boolean, default=False)

    # Relationships
    role = relationship("Role", back_populates="permissions")
    module = relationship("Module", back_populates="role_permissions")

    # Unique constraint
    __table_args__ = (UniqueConstraint('role_id', 'module_id', name='uq_role_module'),)