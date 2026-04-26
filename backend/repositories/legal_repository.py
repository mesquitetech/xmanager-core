"""
Repository layer for legal operations
Handles all database interactions for contracts and legal information
"""

from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, text
from datetime import datetime, date, timedelta
import uuid

from models import Contract, ContractDocument, Site, SiteLegalInfo, User

def get_contracts_with_pagination(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    search: Optional[str] = None,
    status: Optional[str] = None,
    contract_type: Optional[str] = None,
    site_id: Optional[uuid.UUID] = None
) -> Tuple[List[Dict[str, Any]], int]:
    """Get contracts with pagination and filters"""
    try:
        query = db.query(Contract).join(Site, Contract.site_id == Site.id, isouter=True)
        
        # Apply filters
        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    Contract.title.ilike(search_term),
                    Contract.related_party.ilike(search_term),
                    Site.name.ilike(search_term),
                    Site.code.ilike(search_term)
                )
            )
        
        if status:
            query = query.filter(Contract.status == status)
            
        if contract_type:
            query = query.filter(Contract.type == contract_type)
            
        if site_id:
            query = query.filter(Contract.site_id == site_id)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and get results
        contracts = query.offset(skip).limit(limit).all()
        
        # Convert to dict format with site information
        results = []
        for contract in contracts:
            contract_dict = {
                "id": contract.id,
                "title": contract.title,
                "type": contract.type,
                "related_party": contract.related_party,
                "start_date": contract.start_date,
                "end_date": contract.end_date, 
                "value": contract.value,
                "status": contract.status,
                "site_id": contract.site_id,
                "site_name": contract.site.name if contract.site else None,
                "description": contract.description,
                "created_at": contract.created_at,
                "updated_at": contract.updated_at,
                "created_by_id": contract.created_by_id,
                "documents_count": 0  # TODO: Count documents
            }
            results.append(contract_dict)
        
        return results, total
        
    except Exception as e:
        print(f"Error getting contracts: {e}")
        return [], 0

def get_contract_by_id(db: Session, contract_id: uuid.UUID) -> Optional[Dict[str, Any]]:
    """Get contract by ID with related site information"""
    try:
        contract = db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            return None
            
        site = db.query(Site).filter(Site.id == contract.site_id).first() if contract.site_id else None
        
        return {
            "id": contract.id,
            "title": contract.title,
            "type": contract.type,
            "related_party": contract.related_party,
            "start_date": contract.start_date,
            "end_date": contract.end_date,
            "value": contract.value,
            "status": contract.status,
            "site_id": contract.site_id,
            "site_name": site.name if site else None,
            "description": contract.description,
            "created_at": contract.created_at,
            "updated_at": contract.updated_at,
            "created_by_id": contract.created_by_id,
            "documents_count": 0  # TODO: Count documents
        }
        
    except Exception as e:
        print(f"Error getting contract by ID: {e}")
        return None

def create_contract(db: Session, contract_data: Dict[str, Any], user_id: uuid.UUID) -> Optional[Dict[str, Any]]:
    """Create new contract"""
    try:
        contract = Contract(
            title=contract_data["title"],
            type=contract_data["type"],
            related_party=contract_data["related_party"],
            start_date=contract_data["start_date"],
            end_date=contract_data["end_date"],
            value=contract_data["value"],
            status=contract_data["status"],
            site_id=contract_data.get("site_id"),
            description=contract_data.get("description"),
            created_by_id=user_id
        )
        
        db.add(contract)
        db.commit()
        db.refresh(contract)
        
        return get_contract_by_id(db, contract.id)
        
    except Exception as e:
        db.rollback()
        print(f"Error creating contract: {e}")
        return None

def update_contract(db: Session, contract_id: uuid.UUID, contract_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update existing contract"""
    try:
        contract = db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            return None
            
        # Update fields
        for field, value in contract_data.items():
            if value is not None and hasattr(contract, field):
                setattr(contract, field, value)
        
        contract.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(contract)
        
        return get_contract_by_id(db, contract.id)
        
    except Exception as e:
        db.rollback()
        print(f"Error updating contract: {e}")
        return None

def delete_contract(db: Session, contract_id: uuid.UUID) -> bool:
    """Delete contract"""
    try:
        contract = db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            return False
            
        db.delete(contract)
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"Error deleting contract: {e}")
        return False

def get_site_legal_info_by_site_id(db: Session, site_id: uuid.UUID) -> Optional[Dict[str, Any]]:
    """Get site legal information by site ID"""
    try:
        site_legal = db.query(SiteLegalInfo).filter(SiteLegalInfo.site_id == site_id).first()
        if not site_legal:
            return None
            
        site = db.query(Site).filter(Site.id == site_id).first()
        
        return {
            "id": site_legal.id,
            "site_id": site_legal.site_id,
            "site_name": site.name if site else None,
            "contract_start_date": site_legal.contract_start_date,
            "contract_end_date": site_legal.contract_end_date,
            "contract_document_path": site_legal.contract_document_path,
            "monthly_rent": site_legal.monthly_rent,
            "currency": site_legal.currency,
            "landlord_name": site_legal.landlord_name,
            "landlord_contact": site_legal.landlord_contact,
            "landlord_email": site_legal.landlord_email,
            "payment_frequency": site_legal.payment_frequency,
            "next_payment_date": site_legal.next_payment_date,
            "payment_status": site_legal.payment_status,
            "payment_evidence_file": site_legal.payment_evidence_file,
            "payment_evidence_type": site_legal.payment_evidence_type,
            "service_provider": site_legal.service_provider,
            "service_provider_contact": site_legal.service_provider_contact,
            "service_provider_email": site_legal.service_provider_email,
            "created_at": site_legal.created_at,
            "updated_at": site_legal.updated_at
        }
        
    except Exception as e:
        print(f"Error getting site legal info: {e}")
        return None

def create_or_update_site_legal_info(db: Session, site_id: uuid.UUID, legal_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Create or update site legal information"""
    try:
        site_legal = db.query(SiteLegalInfo).filter(SiteLegalInfo.site_id == site_id).first()
        
        if site_legal:
            # Update existing
            for field, value in legal_data.items():
                if hasattr(site_legal, field):
                    setattr(site_legal, field, value)
            site_legal.updated_at = datetime.utcnow()
        else:
            # Create new
            site_legal = SiteLegalInfo(site_id=site_id, **legal_data)
            db.add(site_legal)
        
        db.commit()
        db.refresh(site_legal)
        
        return get_site_legal_info_by_site_id(db, site_id)
        
    except Exception as e:
        db.rollback()
        print(f"Error creating/updating site legal info: {e}")
        return None

def get_legal_statistics(db: Session) -> Dict[str, Any]:
    """Get legal/contract statistics"""
    try:
        stats = {
            "total_contracts": 0,
            "active_contracts": 0,
            "expired_contracts": 0,
            "expiring_soon": 0,
            "total_monthly_rent": 0.0,
            "pending_payments": 0
        }
        
        # Contract statistics
        total_contracts = db.query(func.count(Contract.id)).scalar() or 0
        active_contracts = db.query(func.count(Contract.id)).filter(Contract.status == "active").scalar() or 0
        expired_contracts = db.query(func.count(Contract.id)).filter(Contract.status == "expired").scalar() or 0
        
        # Expiring soon (within 30 days)
        future_date = datetime.now() + timedelta(days=30)
        expiring_soon = db.query(func.count(Contract.id)).filter(
            and_(Contract.end_date <= future_date, Contract.status == "active")
        ).scalar() or 0
        
        stats.update({
            "total_contracts": total_contracts,
            "active_contracts": active_contracts,
            "expired_contracts": expired_contracts,
            "expiring_soon": expiring_soon
        })
        
        # Site legal info statistics
        total_rent = db.query(func.sum(SiteLegalInfo.monthly_rent)).scalar() or 0.0
        pending_payments = db.query(func.count(SiteLegalInfo.id)).filter(
            SiteLegalInfo.payment_status == "unpaid"
        ).scalar() or 0
        
        stats.update({
            "total_monthly_rent": float(total_rent),
            "pending_payments": pending_payments
        })
        
        return stats
        
    except Exception as e:
        print(f"Error getting legal statistics: {e}")
        return {
            "total_contracts": 0,
            "active_contracts": 0,
            "expired_contracts": 0,
            "expiring_soon": 0,
            "total_monthly_rent": 0.0,
            "pending_payments": 0
        }

def get_site_by_id(db: Session, site_id: uuid.UUID) -> Optional[Dict[str, Any]]:
    """Get site information by ID"""
    try:
        site = db.query(Site).filter(Site.id == site_id).first()
        if not site:
            return None
        return {
            "id": site.id,
            "name": site.name,
            "code": site.code,
            "address": site.address,
            "city": site.city,
            "state": site.state
        }
    except Exception as e:
        print(f"Error getting site: {e}")
        return None