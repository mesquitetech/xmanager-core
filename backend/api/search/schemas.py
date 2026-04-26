from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class SiteCandidateBase(BaseModel):
    name: Optional[str] = None
    address: str
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    latitude: float
    longitude: float
    estimated_monthly_rent: Optional[float] = None
    currency: str = "USD"
    owner_contact_name: Optional[str] = None
    owner_contact_phone: Optional[str] = None
    owner_contact_email: Optional[str] = None
    site_type: Optional[str] = None
    status: str = "pending"
    photos: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class SiteCandidateCreate(SiteCandidateBase):
    search_request_id: UUID

class SiteCandidateUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    estimated_monthly_rent: Optional[float] = None
    currency: Optional[str] = None
    owner_contact_name: Optional[str] = None
    owner_contact_phone: Optional[str] = None
    owner_contact_email: Optional[str] = None
    site_type: Optional[str] = None
    status: Optional[str] = None
    photos: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class SiteCandidate(SiteCandidateBase):
    id: UUID
    search_request_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SiteSearchRequestBase(BaseModel):
    title: str
    description: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    coverage_radius_km: Optional[float] = None
    target_latitude: Optional[float] = None
    target_longitude: Optional[float] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    currency: str = "USD"
    site_type: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str = "new"
    requirements: Optional[Dict[str, Any]] = None
    attachments: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class SiteSearchRequestCreate(SiteSearchRequestBase):
    pass

class SiteSearchRequestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    coverage_radius_km: Optional[float] = None
    target_latitude: Optional[float] = None
    target_longitude: Optional[float] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    currency: Optional[str] = None
    site_type: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None
    requirements: Optional[Dict[str, Any]] = None
    attachments: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class SiteSearchRequest(SiteSearchRequestBase):
    id: UUID
    requested_by_id: UUID
    requested_by_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    candidates: List[SiteCandidate] = []
    
    class Config:
        from_attributes = True

class SiteSearchRequestList(BaseModel):
    items: List[SiteSearchRequest]
    total: int
    page: int
    size: int
    pages: int
