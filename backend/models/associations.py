from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from db.database import Base

# Association tables for many-to-many relationships
site_equipment = Table(
    'site_equipment',
    Base.metadata,
    Column('site_id', UUID(as_uuid=True), ForeignKey('sites.id'), primary_key=True),
    Column('equipment_id', UUID(as_uuid=True), ForeignKey('equipment.id'), primary_key=True)
)