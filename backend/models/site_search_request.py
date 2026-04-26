import uuid
from sqlalchemy import Column, String, Float, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from db.database import Base

class SiteSearchRequest(Base):
    __tablename__ = "site_search_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requested_by = Column(String, nullable=False)
    search_area = Column(String)
    center_latitude = Column(Float)
    center_longitude = Column(Float)
    search_radius = Column(Float)
    site_type_needed = Column(String)
    min_height = Column(Float)
    max_height = Column(Float)
    coverage_requirements = Column(Text)
    budget_range = Column(String)
    timeline = Column(String)
    status = Column(String, default="pending")
    assigned_to = Column(String)
    is_completed = Column(Boolean, default=False)
    completion_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())