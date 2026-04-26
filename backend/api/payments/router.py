"""
API Router for Payment Evidence operations
Clean architecture implementation - only handles HTTP layer
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from db.database import get_db
from auth.utils import get_current_user, User
from utils.storage import upload_file, create_signed_url, BUCKETS
from api.payments.schemas import (
    PaymentEvidenceRequest, PaymentEvidenceResponse, PaymentEvidenceListResponse,
    PaymentEvidenceUploadResponse, PaymentEvidenceUpdateResponse,
    PaymentEvidenceDeleteResponse, PaymentStatusBatchResponse,
    PaymentEvidenceBatchResponse, PaymentNotificationCheckResponse
)
from services.payment_service import (
    get_payment_evidence_logic,
    upload_payment_evidence_logic,
    update_payment_evidence_logic,
    delete_payment_evidence_logic,
    get_site_payment_evidences_logic,
    get_payment_evidences_status_logic,
    get_payment_evidences_batch_logic
)

router = APIRouter()

@router.get("/api/payments/evidence/{site_id}", response_model=PaymentEvidenceResponse)
async def get_payment_evidence(
    site_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment evidence for a specific site"""
    return get_payment_evidence_logic(db, site_id, current_user.id)

@router.post("/api/payments/evidence/{site_id}", response_model=PaymentEvidenceUploadResponse)
async def upload_payment_evidence(
    site_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload payment evidence for a site to Supabase Storage"""
    try:
        file_bytes = await file.read()
        content_type = file.content_type or "application/octet-stream"
        path = upload_file(
            bucket=BUCKETS["pagos"],
            file_bytes=file_bytes,
            filename=file.filename,
            content_type=content_type,
            folder=str(site_id),
        )
        file_data = PaymentEvidenceRequest(
            file_name=file.filename,
            file_type=content_type,
            file_url=path,  # guardamos el path, la signed URL se genera al servir
        )
        result = upload_payment_evidence_logic(db, site_id, file_data, current_user.id)
        db.commit()
        return result
    except Exception as e:
        db.rollback()
        raise e

@router.put("/api/payments/evidence/{evidence_id}", response_model=PaymentEvidenceUpdateResponse)
async def update_payment_evidence(
    evidence_id: UUID,
    file_data: PaymentEvidenceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update existing payment evidence"""
    try:
        result = update_payment_evidence_logic(db, evidence_id, file_data, current_user.id)
        db.commit()
        return result
    except Exception as e:
        db.rollback()
        raise e

@router.delete("/api/payments/evidence/{evidence_id}", response_model=PaymentEvidenceDeleteResponse)
async def delete_payment_evidence(
    evidence_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete payment evidence"""
    try:
        result = delete_payment_evidence_logic(db, evidence_id, current_user.id)
        db.commit()
        return result
    except Exception as e:
        db.rollback()
        raise e

@router.get("/api/payments/evidences/site/{site_id}", response_model=PaymentEvidenceListResponse)
async def get_site_payment_evidences(
    site_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all payment evidences for a specific site"""
    return get_site_payment_evidences_logic(db, site_id, current_user.id)

@router.post("/api/payments/evidences/status", response_model=PaymentStatusBatchResponse)
async def get_payment_evidences_status(
    site_ids: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment evidence status for multiple sites in batch"""
    return get_payment_evidences_status_logic(db, site_ids, current_user.id)

# Legacy notification endpoints - to be moved to dedicated notification service

@router.post("/api/payments/evidences/batch", response_model=PaymentEvidenceBatchResponse)
async def get_payment_evidences_batch(
    evidence_ids: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get multiple payment evidences in batch"""
    return get_payment_evidences_batch_logic(db, evidence_ids, current_user.id)