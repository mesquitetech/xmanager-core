from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import uuid

from db.database import get_db
from auth.utils import get_current_user
from models import User
from . import schemas
from services.legal_service import (
    get_contracts_logic,
    get_contract_logic,
    create_contract_logic,
    update_contract_logic,
    delete_contract_logic,
    get_site_legal_info_logic,
    create_site_legal_info_logic,
    update_site_legal_info_logic,
    get_legal_statistics_logic
)
from repositories.legal_repository import get_contracts_with_pagination

router = APIRouter(tags=["legal"])

# Contract endpoints
@router.get("/contracts")
async def get_contracts(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term"),
    status: Optional[str] = Query(None, description="Contract status filter"),
    type: Optional[str] = Query(None, description="Contract type filter"),
    site_id: Optional[uuid.UUID] = Query(None, description="Site ID filter"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get contracts with pagination and filters - returns array for frontend compatibility"""
    try:
        contracts, total = get_contracts_with_pagination(
            db, 
            skip=(page - 1) * size, 
            limit=size, 
            search=search, 
            status=status, 
            contract_type=type, 
            site_id=site_id
        )
        return contracts  # Return array directly for frontend compatibility
    except Exception as e:
        print(f"Error in get_contracts endpoint: {e}")
        return []  # Return empty array on error

@router.get("/contracts/{contract_id}", response_model=schemas.ContractResponse)
async def get_contract(
    contract_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get contract by ID"""
    return get_contract_logic(db, contract_id)

@router.post("/contracts", response_model=schemas.ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(
    contract: schemas.ContractCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new contract"""
    return create_contract_logic(db, contract, current_user.id)

@router.put("/contracts/{contract_id}", response_model=schemas.ContractResponse)
async def update_contract(
    contract_id: uuid.UUID,
    contract: schemas.ContractUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update contract"""
    return update_contract_logic(db, contract_id, contract)

@router.delete("/contracts/{contract_id}")
async def delete_contract(
    contract_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete contract"""
    return delete_contract_logic(db, contract_id)

# Site Legal Info endpoints
@router.get("/sites/{site_id}/legal", response_model=Optional[schemas.SiteLegalInfoResponse])
async def get_site_legal_info(
    site_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get site legal information"""
    return get_site_legal_info_logic(db, site_id)

@router.post("/sites/{site_id}/legal", response_model=schemas.SiteLegalInfoResponse, status_code=status.HTTP_201_CREATED)
async def create_site_legal_info(
    site_id: uuid.UUID,
    legal_info: schemas.SiteLegalInfoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create site legal information"""
    # Override site_id from URL
    legal_info.site_id = site_id
    return create_site_legal_info_logic(db, legal_info)

@router.put("/sites/{site_id}/legal", response_model=schemas.SiteLegalInfoResponse)
async def update_site_legal_info(
    site_id: uuid.UUID,
    legal_info: schemas.SiteLegalInfoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update site legal information"""
    return update_site_legal_info_logic(db, site_id, legal_info)

# Statistics endpoint
@router.get("/statistics", response_model=schemas.LegalStatistics)
async def get_legal_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get legal and contract statistics"""
    return get_legal_statistics_logic(db)