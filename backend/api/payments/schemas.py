"""
Pydantic schemas for Payments API
Defines request/response models and validation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class PaymentEvidenceRequest(BaseModel):
    """Request model for uploading payment evidence via file upload"""
    file_name: str = Field(..., description="Name of the uploaded file")
    file_type: str = Field(..., description="MIME type of the file")
    file_data: Optional[str] = Field(None, description="Base64 encoded file data (legacy)")
    file_url: Optional[str] = Field(None, description="URL in Supabase Storage")


class PaymentEvidenceResponse(BaseModel):
    """Response model for payment evidence"""
    id: str
    site_id: str
    file_name: str
    file_type: str
    file_url: Optional[str] = None   # URL en Supabase Storage
    file_data: Optional[str] = None  # Legacy: Base64
    uploaded_by_id: Optional[str] = None
    uploaded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaymentEvidenceListItem(BaseModel):
    """List item model for payment evidence (without file data)"""
    id: str
    site_id: str
    file_name: str
    file_type: str
    uploaded_by_id: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PaymentEvidenceStatusRequest(BaseModel):
    """Request model for checking payment evidence status"""
    site_ids: List[str] = Field(..., description="List of site IDs to check")


class PaymentEvidenceStatusResponse(BaseModel):
    """Response model for payment evidence status"""
    site_id: str
    has_evidence: bool
    evidence_id: Optional[str] = None
    last_updated: Optional[datetime] = None


class PaymentEvidenceBatchRequest(BaseModel):
    """Request model for batch evidence retrieval"""
    evidence_ids: List[str] = Field(..., description="List of evidence IDs to retrieve")


class PaymentEvidenceUploadResponse(BaseModel):
    """Response model for successful evidence upload"""
    success: bool
    message: str
    evidence_id: str
    next_payment_date: Optional[str] = None


class PaymentEvidenceUpdateResponse(BaseModel):
    """Response model for evidence update"""
    success: bool
    message: str
    evidence_id: str


class PaymentEvidenceDeleteResponse(BaseModel):
    """Response model for evidence deletion"""
    success: bool
    message: str
    next_payment_date: Optional[str] = None


class PaymentNotificationCheckResponse(BaseModel):
    """Response model for payment notification check"""
    success: bool
    message: str
    pending_notifications: int
    overdue_notifications: int
    total_notifications: int


class PaymentStatusBatchResponse(BaseModel):
    """Response model for batch status check"""
    status: List[PaymentEvidenceStatusResponse]


class PaymentEvidenceBatchResponse(BaseModel):
    """Response model for batch evidence retrieval"""
    evidences: List[PaymentEvidenceResponse]


class PaymentEvidenceListResponse(BaseModel):
    """Response model for evidence list"""
    evidences: List[PaymentEvidenceResponse]


# Validation schemas
class PaymentFrequency(BaseModel):
    """Model for payment frequency validation"""
    frequency: str
    
    @validator('frequency')
    def validate_frequency(cls, v):
        valid_frequencies = [
            'Mensual', 'Quincenal', 'Semanal', 'Trimestral', 
            'Bimestral', 'Anual', 'Pago Único',
            'monthly', 'biweekly', 'weekly', 'quarterly',
            'bimonthly', 'yearly', 'annual'
        ]
        if v not in valid_frequencies:
            raise ValueError('Invalid payment frequency')
        return v


class PaymentCalculationRequest(BaseModel):
    """Request model for payment date calculations"""
    current_date: Optional[datetime] = None
    frequency: str
    
    @validator('frequency')
    def validate_frequency(cls, v):
        return PaymentFrequency(frequency=v).frequency