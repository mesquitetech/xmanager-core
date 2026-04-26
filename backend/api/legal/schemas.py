from pydantic import BaseModel, validator, Field, field_validator
from typing import Optional, List
import uuid
from datetime import datetime, date

# Contract Base Models
class ContractBase(BaseModel):
    title: str
    type: str
    related_party: str  # Campo para arrendador/parte relacionada 
    start_date: date
    end_date: date
    value: float = Field(gt=0)  # Valor del contrato
    status: str
    site_id: Optional[uuid.UUID] = None
    description: Optional[str] = None

  
    @field_validator('end_date')
    @classmethod
    def end_date_must_be_after_start_date(cls, v, values, **kwargs):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return v

class ContractCreate(ContractBase):
    pass

class ContractUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    related_party: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    value: Optional[float] = None
    status: Optional[str] = None
    site_id: Optional[uuid.UUID] = None
    description: Optional[str] = None

class ContractResponse(BaseModel):
    id: uuid.UUID
    title: str
    type: str
    related_party: str  # Campo para arrendador/parte relacionada
    start_date: date
    end_date: date
    value: float  # Valor del contrato
    status: str
    site_id: Optional[uuid.UUID] = None
    site_name: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: Optional[uuid.UUID] = None
    documents_count: int = 0
    
    class Config:
        from_attributes = True

# Contract Document Models
class ContractDocumentBase(BaseModel):
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    description: Optional[str] = None
    document_type: Optional[str] = None

class ContractDocumentCreate(ContractDocumentBase):
    contract_id: uuid.UUID

class ContractDocumentResponse(ContractDocumentBase):
    id: uuid.UUID
    contract_id: uuid.UUID
    uploaded_at: datetime
    uploaded_by_id: Optional[uuid.UUID] = None
    
    class Config:
        from_attributes = True

# Site Legal Info Models
class SiteLegalInfoBase(BaseModel):
    contract_start_date: Optional[datetime] = None
    contract_end_date: Optional[datetime] = None
    contract_document_path: Optional[str] = None
    monthly_rent: Optional[float] = None
    currency: Optional[str] = "USD"
    landlord_name: Optional[str] = None
    landlord_contact: Optional[str] = None
    landlord_email: Optional[str] = None
    payment_frequency: Optional[str] = "monthly"
    next_payment_date: Optional[datetime] = None
    payment_status: Optional[str] = "unpaid"
    payment_evidence_file: Optional[str] = None
    payment_evidence_type: Optional[str] = None
    service_provider: Optional[str] = None
    service_provider_contact: Optional[str] = None
    service_provider_email: Optional[str] = None

class SiteLegalInfoCreate(SiteLegalInfoBase):
    site_id: uuid.UUID

class SiteLegalInfoUpdate(SiteLegalInfoBase):
    pass

class SiteLegalInfoResponse(SiteLegalInfoBase):
    id: uuid.UUID
    site_id: uuid.UUID
    site_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Enhanced Contract Models for Extended Functionality
class EnhancedContractResponse(BaseModel):
    id: uuid.UUID
    site_id: uuid.UUID
    site_name: str
    site_address: Optional[str] = None
    landlord_name: Optional[str] = None
    landlord_contact: Optional[str] = None
    landlord_email: Optional[str] = None
    landlord_phone: Optional[str] = None
    contract_date: Optional[datetime] = None
    contract_start_date: Optional[datetime] = None
    contract_end_date: Optional[datetime] = None
    monthly_rent: float = 0.0
    currency: str = "USD"
    requires_invoice: str = "NO"
    courtesy_service: str = "NO"
    courtesy_service_details: Optional[str] = None
    payment_frequency: str = "monthly"
    next_payment_date: Optional[datetime] = None
    notes: Optional[str] = None
    contract_status: str
    days_to_expiration: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Filter and Search Models
class ContractFilters(BaseModel):
    search: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    site_id: Optional[uuid.UUID] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class LegalFilters(BaseModel):
    search: Optional[str] = None
    invoice_filter: Optional[str] = None
    courtesy_filter: Optional[str] = None
    
# Pagination Models
class ContractList(BaseModel):
    items: List[ContractResponse]
    total: int
    page: int
    size: int
    pages: int

class EnhancedContractList(BaseModel):
    items: List[EnhancedContractResponse]
    total: int
    page: int
    size: int
    pages: int

# Statistics Models
class LegalStatistics(BaseModel):
    total_contracts: int = 0
    active_contracts: int = 0
    expired_contracts: int = 0
    expiring_soon: int = 0  # Within 30 days
    total_monthly_rent: float = 0.0
    pending_payments: int = 0
    
    class Config:
        from_attributes = True