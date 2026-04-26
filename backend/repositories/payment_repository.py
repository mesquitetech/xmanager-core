"""
Repository layer for Payment operations
Handles all database interactions for payments and evidence
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from uuid import UUID
from datetime import datetime

from models import PaymentEvidence, Site, SiteLegalInfo
from api.payments.schemas import PaymentEvidenceRequest


def get_payment_evidence_by_site_id(db: Session, site_id: UUID) -> Optional[PaymentEvidence]:
    """Get the most recent payment evidence for a site"""
    return db.query(PaymentEvidence)\
        .filter(PaymentEvidence.site_id == site_id)\
        .order_by(desc(PaymentEvidence.uploaded_at))\
        .first()


def get_all_payment_evidences_by_site_id(db: Session, site_id: UUID) -> List[PaymentEvidence]:
    """Get all payment evidences for a site"""
    return db.query(PaymentEvidence)\
        .filter(PaymentEvidence.site_id == site_id)\
        .order_by(desc(PaymentEvidence.uploaded_at))\
        .all()


def get_payment_evidence_by_id(db: Session, evidence_id: UUID) -> Optional[PaymentEvidence]:
    """Get payment evidence by ID"""
    return db.query(PaymentEvidence)\
        .filter(PaymentEvidence.id == evidence_id)\
        .first()


def get_payment_evidences_by_ids(db: Session, evidence_ids: List[UUID]) -> List[PaymentEvidence]:
    """Get multiple payment evidences by IDs"""
    return db.query(PaymentEvidence)\
        .filter(PaymentEvidence.id.in_(evidence_ids))\
        .all()


def create_payment_evidence(
    db: Session,
    site_id: UUID,
    file_data: PaymentEvidenceRequest,
    user_id: UUID
) -> PaymentEvidence:
    """Create new payment evidence"""
    new_evidence = PaymentEvidence(
        site_id=site_id,
        file_name=file_data.file_name,
        file_type=file_data.file_type,
        file_url=file_data.file_url,
        file_data=file_data.file_data,  # None para uploads nuevos
        uploaded_by_id=user_id,
        uploaded_at=datetime.utcnow()
    )

    db.add(new_evidence)
    return new_evidence


def update_payment_evidence(
    db: Session,
    evidence: PaymentEvidence,
    file_data: PaymentEvidenceRequest,
    user_id: UUID
) -> PaymentEvidence:
    """Update existing payment evidence"""
    evidence.file_name = file_data.file_name
    evidence.file_type = file_data.file_type
    evidence.file_url = file_data.file_url
    evidence.file_data = file_data.file_data  # None para uploads nuevos
    evidence.uploaded_by_id = user_id
    evidence.uploaded_at = datetime.utcnow()

    return evidence


def delete_payment_evidence(db: Session, evidence: PaymentEvidence) -> None:
    """Delete payment evidence"""
    db.delete(evidence)


def get_site_by_id(db: Session, site_id: UUID) -> Optional[Site]:
    """Get site by ID"""
    return db.query(Site).filter(Site.id == site_id).first()


def get_site_legal_info_by_site_id(db: Session, site_id: UUID) -> Optional[SiteLegalInfo]:
    """Get site legal information by site ID"""
    return db.query(SiteLegalInfo)\
        .filter(SiteLegalInfo.site_id == site_id)\
        .first()


def update_site_legal_payment_status(
    db: Session, 
    site_legal_info: SiteLegalInfo, 
    payment_status: str, 
    next_payment_date: Optional[datetime] = None
) -> SiteLegalInfo:
    """Update site legal payment status and next payment date"""
    site_legal_info.payment_status = payment_status
    if next_payment_date:
        site_legal_info.next_payment_date = next_payment_date
    
    return site_legal_info


def get_payment_evidences_status_batch(
    db: Session, 
    site_ids: List[UUID]
) -> List[PaymentEvidence]:
    """Get payment evidence status for multiple sites efficiently"""
    # Get the most recent evidence for each site
    from sqlalchemy import func
    
    # Use window function to get the most recent evidence per site
    recent_evidences = db.query(PaymentEvidence).filter(
        PaymentEvidence.site_id.in_(site_ids)
    ).order_by(
        PaymentEvidence.site_id,
        desc(PaymentEvidence.uploaded_at)
    ).all()
    
    # Filter to get only the most recent per site
    seen_sites = set()
    result = []
    for evidence in recent_evidences:
        if evidence.site_id not in seen_sites:
            result.append(evidence)
            seen_sites.add(evidence.site_id)
    
    return result


def validate_site_exists(db: Session, site_id: UUID) -> bool:
    """Check if site exists"""
    site = db.query(Site).filter(Site.id == site_id).first()
    return site is not None


def validate_site_has_legal_info(db: Session, site_id: UUID) -> bool:
    """Check if site has legal information configured"""
    site = db.query(Site).filter(Site.id == site_id).first()
    return site is not None and site.legal_info is not None


def get_sites_for_payment_notifications(db: Session) -> List[Site]:
    """Get sites that need payment notifications (pending/overdue)"""
    current_date = datetime.utcnow()
    
    # Get sites with upcoming payments (next 7 days) or overdue payments
    sites = db.query(Site).join(
        SiteLegalInfo, Site.id == SiteLegalInfo.site_id
    ).filter(
        and_(
            SiteLegalInfo.next_payment_date.isnot(None),
            SiteLegalInfo.payment_status != "paid"
        )
    ).all()
    
    return sites