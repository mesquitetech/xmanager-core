from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, UUID4
from models import IncidentPriority, IncidentStatus

# Pydantic models for Incidents
class IncidentBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    priority: IncidentPriority = IncidentPriority.MEDIUM

class IncidentCreate(IncidentBase):
    site_id: UUID4
    attachments: Optional[Union[List[str], str]] = None

class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[IncidentPriority] = None
    status: Optional[IncidentStatus] = None
    assignee_id: Optional[UUID4] = None
    resolution_notes: Optional[str] = None
    attachments: Optional[Union[List[str], str]] = None

class IncidentResponse(IncidentBase):
    id: UUID4
    site_id: UUID4
    site_name: Optional[str] = None
    reporter_id: UUID4
    reporter_name: Optional[str] = None
    assignee_id: Optional[UUID4] = None
    assignee_name: Optional[str] = None
    status: IncidentStatus
    reported_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    attachments: Optional[Union[List[str], str]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Alias for compatibility with existing code
Incident = IncidentResponse

# Pagination response for incident lists
class IncidentList(BaseModel):
    items: List[IncidentResponse]
    total: int
    page: int
    size: int
    pages: int