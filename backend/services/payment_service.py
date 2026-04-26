"""
Service layer for Payment operations
Handles business logic and validation for payments
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta

from repositories.payment_repository import (
    get_payment_evidence_by_site_id,
    get_all_payment_evidences_by_site_id,
    get_payment_evidence_by_id,
    get_payment_evidences_by_ids,
    create_payment_evidence,
    update_payment_evidence,
    delete_payment_evidence,
    get_site_by_id,
    get_site_legal_info_by_site_id,
    update_site_legal_payment_status,
    get_payment_evidences_status_batch,
    validate_site_exists,
    validate_site_has_legal_info
)
from api.payments.schemas import (
    PaymentEvidenceRequest, PaymentEvidenceResponse, PaymentEvidenceListItem,
    PaymentEvidenceUploadResponse, PaymentEvidenceUpdateResponse,
    PaymentEvidenceDeleteResponse, PaymentEvidenceStatusResponse,
    PaymentStatusBatchResponse, PaymentEvidenceBatchResponse,
    PaymentEvidenceListResponse
)
from services.notification_service import create_payment_notification
from utils.storage import create_signed_url, BUCKETS


def _resolve_file_url(file_url: Optional[str]) -> Optional[str]:
    """
    Convierte un path de Storage en una signed URL temporal.
    Si file_url ya es una URL completa (legacy), la devuelve tal cual.
    Si es None, devuelve None.
    """
    if not file_url:
        return None
    if file_url.startswith("http"):
        return file_url  # registro legacy con URL directa
    try:
        return create_signed_url(BUCKETS["pagos"], file_url)
    except Exception:
        return None


def calculate_next_payment_date(current_date: Optional[datetime], frequency: str) -> datetime:
    """Calculate next payment date based on frequency"""
    # If no current date provided, use current time
    if not current_date:
        current_date = datetime.now(timezone.utc)
    
    if isinstance(current_date, str):
        current_date = datetime.fromisoformat(current_date.replace('Z', '+00:00'))
    
    # Normalize frequency to Spanish terms
    frequency_mapping = {
        "monthly": "Mensual",
        "biweekly": "Quincenal", 
        "weekly": "Semanal",
        "quarterly": "Trimestral",
        "bimonthly": "Bimestral",
        "yearly": "Anual",
        "annual": "Anual"
    }
    
    normalized_frequency = frequency_mapping.get(frequency.lower(), frequency)
    
    # Calculate next payment date
    if normalized_frequency == "Mensual":
        return current_date + relativedelta(months=1)
    elif normalized_frequency == "Quincenal":
        return current_date + timedelta(days=15)
    elif normalized_frequency == "Semanal":
        return current_date + timedelta(days=7)
    elif normalized_frequency == "Trimestral":
        return current_date + relativedelta(months=3)
    elif normalized_frequency == "Bimestral":
        return current_date + relativedelta(months=2)
    elif normalized_frequency == "Anual":
        return current_date + relativedelta(years=1)
    else:  # Default to monthly for "Pago Único" or unrecognized values
        return current_date + relativedelta(months=1)


def reverse_payment_date_calculation(current_date: datetime, frequency: str) -> datetime:
    """Reverse calculate payment date (subtract instead of add)"""
    # Normalize frequency
    frequency_mapping = {
        "monthly": "Mensual",
        "biweekly": "Quincenal",
        "weekly": "Semanal", 
        "quarterly": "Trimestral",
        "bimonthly": "Bimestral",
        "yearly": "Anual",
        "annual": "Anual"
    }
    
    normalized_frequency = frequency_mapping.get(frequency.lower(), frequency)
    
    # Reverse calculation (subtract time)
    if normalized_frequency == "Mensual":
        return current_date - relativedelta(months=1)
    elif normalized_frequency == "Quincenal":
        return current_date - timedelta(days=15)
    elif normalized_frequency == "Semanal":
        return current_date - timedelta(days=7)
    elif normalized_frequency == "Trimestral":
        return current_date - relativedelta(months=3)
    elif normalized_frequency == "Bimestral":
        return current_date - relativedelta(months=2)
    elif normalized_frequency == "Anual":
        return current_date - relativedelta(years=1)
    else:  # Default to monthly
        return current_date - relativedelta(months=1)


def get_payment_evidence_logic(db: Session, site_id: UUID, user_id: UUID) -> PaymentEvidenceResponse:
    """Get most recent payment evidence for a site"""
    # Validate site exists
    if not validate_site_exists(db, site_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sitio no encontrado"
        )
    
    # Get evidence
    evidence = get_payment_evidence_by_site_id(db, site_id)
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró evidencia de pago para este sitio"
        )
    
    return PaymentEvidenceResponse(
        id=str(evidence.id),
        site_id=str(evidence.site_id),
        file_name=evidence.file_name,
        file_type=evidence.file_type,
        file_url=_resolve_file_url(evidence.file_url),
        file_data=evidence.file_data,
        uploaded_by_id=str(evidence.uploaded_by_id) if evidence.uploaded_by_id else None,
        uploaded_at=evidence.uploaded_at
    )


def upload_payment_evidence_logic(
    db: Session, 
    site_id: UUID, 
    file_data: PaymentEvidenceRequest, 
    user_id: UUID
) -> PaymentEvidenceUploadResponse:
    """Upload payment evidence for a site"""
    # Validate site exists
    if not validate_site_exists(db, site_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sitio no encontrado"
        )
    
    # Validate site has legal info
    if not validate_site_has_legal_info(db, site_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El sitio no tiene información legal configurada"
        )
    
    try:
        # Create evidence
        new_evidence = create_payment_evidence(db, site_id, file_data, user_id)
        
        # Update payment status and calculate next payment date
        site_legal_info = get_site_legal_info_by_site_id(db, site_id)
        next_payment_date = None
        
        if site_legal_info:
            # Update status to paid
            current_date = datetime.now(timezone.utc)
            current_next_payment = site_legal_info.next_payment_date
            frequency = site_legal_info.payment_frequency or "Mensual"
            
            # Use current date if no next payment date or it's in the past
            if not current_next_payment or current_next_payment < current_date:
                current_next_payment = current_date
            
            # Calculate new next payment date
            next_payment_date = calculate_next_payment_date(current_next_payment, frequency)
            update_site_legal_payment_status(
                db, site_legal_info, "paid", next_payment_date
            )
        
        # Create payment notification
        site = get_site_by_id(db, site_id)
        if site and site_legal_info:
            try:
                create_payment_notification(
                    db=db,
                    action="paid",
                    site_name=site.name,
                    site_id=site_id,
                    amount=float(site_legal_info.monthly_rent) if site_legal_info.monthly_rent else None,
                    created_by_id=user_id
                )
            except Exception as e:
                print(f"Warning: Failed to create payment notification: {e}")
        
        return PaymentEvidenceUploadResponse(
            success=True,
            message="Evidencia de pago subida correctamente",
            evidence_id=str(new_evidence.id),
            next_payment_date=next_payment_date.isoformat() if next_payment_date else None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir evidencia de pago: {str(e)}"
        )


def update_payment_evidence_logic(
    db: Session, 
    evidence_id: UUID, 
    file_data: PaymentEvidenceRequest, 
    user_id: UUID
) -> PaymentEvidenceUpdateResponse:
    """Update existing payment evidence"""
    # Get existing evidence
    evidence = get_payment_evidence_by_id(db, evidence_id)
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidencia de pago no encontrada"
        )
    
    try:
        # Update evidence
        updated_evidence = update_payment_evidence(db, evidence, file_data, user_id)
        
        return PaymentEvidenceUpdateResponse(
            success=True,
            message="Evidencia de pago actualizada correctamente",
            evidence_id=str(updated_evidence.id)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar evidencia de pago: {str(e)}"
        )


def delete_payment_evidence_logic(
    db: Session, 
    evidence_id: UUID, 
    user_id: UUID
) -> PaymentEvidenceDeleteResponse:
    """Delete payment evidence and update payment status"""
    # Get existing evidence
    evidence = get_payment_evidence_by_id(db, evidence_id)
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidencia de pago no encontrada"
        )
    
    try:
        site_id = evidence.site_id
        
        # Get site and legal info for status update and notifications
        site = get_site_by_id(db, site_id)
        site_legal_info = get_site_legal_info_by_site_id(db, site_id)
        
        # Save previous status for notification logic
        previous_status = site_legal_info.payment_status if site_legal_info else None
        
        # Delete evidence
        delete_payment_evidence(db, evidence)
        
        # Update payment status
        next_payment_date = None
        new_status = None
        
        if site_legal_info:
            current_date = datetime.now(timezone.utc)
            payment_date = site_legal_info.next_payment_date
            
            if payment_date:
                # Determine new status based on payment date
                if payment_date < current_date:
                    new_status = "overdue"
                else:
                    new_status = "pending"
                
                # Reverse the payment date calculation
                frequency = site_legal_info.payment_frequency or "Mensual"
                reverted_date = reverse_payment_date_calculation(payment_date, frequency)
                
                # Update status and date
                update_site_legal_payment_status(
                    db, site_legal_info, new_status, reverted_date
                )
                next_payment_date = reverted_date
        
        # Create notification if status changed from paid to pending/overdue
        if (previous_status == "paid" and new_status in ["pending", "overdue"] 
            and site and site_legal_info):
            try:
                create_payment_notification(
                    db=db,
                    action="overdue" if new_status == "overdue" else "pending",
                    site_name=site.name,
                    site_id=site_id,
                    amount=float(site_legal_info.monthly_rent) if site_legal_info.monthly_rent else None,
                    due_date=next_payment_date,
                    created_by_id=user_id
                )
            except Exception as e:
                print(f"Warning: Failed to create payment notification: {e}")
        
        return PaymentEvidenceDeleteResponse(
            success=True,
            message="Evidencia de pago eliminada correctamente",
            next_payment_date=next_payment_date.isoformat() if next_payment_date else None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar evidencia de pago: {str(e)}"
        )


def get_site_payment_evidences_logic(
    db: Session, 
    site_id: UUID, 
    user_id: UUID
) -> PaymentEvidenceListResponse:
    """Get all payment evidences for a site"""
    # Validate site exists
    if not validate_site_exists(db, site_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sitio no encontrado"
        )
    
    # Get all evidences
    evidences = get_all_payment_evidences_by_site_id(db, site_id)
    
    evidence_responses = [
        PaymentEvidenceResponse(
            id=str(evidence.id),
            site_id=str(evidence.site_id),
            file_name=evidence.file_name,
            file_type=evidence.file_type,
            file_url=_resolve_file_url(evidence.file_url),
            file_data=evidence.file_data,
            uploaded_by_id=str(evidence.uploaded_by_id) if evidence.uploaded_by_id else None,
            uploaded_at=evidence.uploaded_at
        ) for evidence in evidences
    ]

    return PaymentEvidenceListResponse(evidences=evidence_responses)


def get_payment_evidences_status_logic(
    db: Session, 
    site_ids: List[str], 
    user_id: UUID
) -> PaymentStatusBatchResponse:
    """Get payment evidence status for multiple sites"""
    # Convert string IDs to UUIDs
    uuids = []
    for site_id in site_ids:
        try:
            uuids.append(UUID(site_id))
        except ValueError:
            continue  # Skip invalid UUIDs
    
    # Get evidence status in batch
    evidences = get_payment_evidences_status_batch(db, uuids)
    
    # Create lookup dictionary
    evidence_dict = {}
    for e in evidences:
        evidence_dict[str(e.site_id)] = {
            "id": str(e.id), 
            "uploaded_at": e.uploaded_at
        }
    
    # Build response
    status_responses = []
    for site_id in site_ids:
        has_evidence = site_id in evidence_dict
        response = PaymentEvidenceStatusResponse(
            site_id=site_id,
            has_evidence=has_evidence
        )
        
        if has_evidence:
            response.evidence_id = evidence_dict[site_id]["id"]
            response.last_updated = evidence_dict[site_id]["uploaded_at"]
            
        status_responses.append(response)
    
    return PaymentStatusBatchResponse(status=status_responses)


def get_payment_evidences_batch_logic(
    db: Session, 
    evidence_ids: List[str], 
    user_id: UUID
) -> PaymentEvidenceBatchResponse:
    """Get multiple payment evidences in batch"""
    # Convert string IDs to UUIDs
    uuids = []
    for evidence_id in evidence_ids:
        try:
            uuids.append(UUID(evidence_id))
        except ValueError:
            continue  # Skip invalid UUIDs
    
    # Get evidences
    evidences = get_payment_evidences_by_ids(db, uuids)
    
    # Create evidence map for ordered response
    evidence_map = {str(e.id): e for e in evidences}
    
    # Build ordered response
    evidence_responses = []
    for evidence_id in evidence_ids:
        if evidence_id in evidence_map:
            evidence = evidence_map[evidence_id]
            evidence_responses.append(PaymentEvidenceResponse(
                id=str(evidence.id),
                site_id=str(evidence.site_id),
                file_name=evidence.file_name,
                file_type=evidence.file_type,
                file_url=_resolve_file_url(evidence.file_url),
                file_data=evidence.file_data,
                uploaded_by_id=str(evidence.uploaded_by_id) if evidence.uploaded_by_id else None,
                uploaded_at=evidence.uploaded_at
            ))
    
    return PaymentEvidenceBatchResponse(evidences=evidence_responses)