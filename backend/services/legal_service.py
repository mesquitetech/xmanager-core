"""
Service layer for legal operations
Handles business logic and validation for contracts and legal information
"""

from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import uuid
import math

from repositories.legal_repository import (
    get_contracts_with_pagination,
    get_contract_by_id,
    create_contract,
    update_contract,
    delete_contract,
    get_site_legal_info_by_site_id,
    create_or_update_site_legal_info,
    get_legal_statistics,
    get_site_by_id
)
from api.legal.schemas import (
    ContractCreate,
    ContractUpdate,
    SiteLegalInfoCreate,
    SiteLegalInfoUpdate,
    ContractFilters,
    ContractList
)


def get_contracts_logic(
    db: Session,
    page: int = 1,
    size: int = 20,
    filters: Optional[ContractFilters] = None
) -> ContractList:
    """Business logic for getting contracts with pagination"""
    
    # Validate pagination parameters
    if page < 1:
        page = 1
    if size < 1 or size > 100:
        size = 20
    
    skip = (page - 1) * size
    
    # Extract filter parameters
    search = filters.search if filters else None
    contract_status = filters.status if filters else None
    contract_type = filters.type if filters else None
    site_id = filters.site_id if filters else None
    
    # Get contracts from repository
    contracts, total = get_contracts_with_pagination(
        db, skip, size, search, contract_status, contract_type, site_id
    )
    
    # Calculate pagination info
    pages = math.ceil(total / size) if total > 0 else 1
    
    return ContractList(
        items=contracts,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


def get_contract_logic(db: Session, contract_id: uuid.UUID) -> Dict[str, Any]:
    """Business logic for getting single contract"""
    contract = get_contract_by_id(db, contract_id)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    return contract


def create_contract_logic(
    db: Session,
    contract_data: ContractCreate,
    current_user_id: uuid.UUID
) -> Dict[str, Any]:
    """Business logic for creating contract"""
    
    # Validate site exists if provided
    if contract_data.site_id:
        site = get_site_by_id(db, contract_data.site_id)
        if not site:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Site not found"
            )
    
    # Convert Pydantic model to dict
    contract_dict = contract_data.dict()
    
    # Create contract
    contract = create_contract(db, contract_dict, current_user_id)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create contract"
        )
    
    return contract


def update_contract_logic(
    db: Session,
    contract_id: uuid.UUID,
    contract_data: ContractUpdate
) -> Dict[str, Any]:
    """Business logic for updating contract"""
    
    # Check if contract exists
    existing_contract = get_contract_by_id(db, contract_id)
    if not existing_contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    # Validate site exists if provided
    if contract_data.site_id:
        site = get_site_by_id(db, contract_data.site_id)
        if not site:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Site not found"
            )
    
    # Convert Pydantic model to dict, excluding None values
    update_data = contract_data.dict(exclude_unset=True)
    
    # Update contract
    contract = update_contract(db, contract_id, update_data)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update contract"
        )
    
    return contract


def delete_contract_logic(db: Session, contract_id: uuid.UUID) -> Dict[str, str]:
    """Business logic for deleting contract"""
    
    # Check if contract exists
    existing_contract = get_contract_by_id(db, contract_id)
    if not existing_contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    # Delete contract
    success = delete_contract(db, contract_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete contract"
        )
    
    return {"message": "Contract deleted successfully"}


def get_site_legal_info_logic(db: Session, site_id: uuid.UUID) -> Optional[Dict[str, Any]]:
    """Business logic for getting site legal information"""
    
    # Validate site exists
    site = get_site_by_id(db, site_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    return get_site_legal_info_by_site_id(db, site_id)


def create_site_legal_info_logic(
    db: Session,
    legal_data: SiteLegalInfoCreate
) -> Dict[str, Any]:
    """Business logic for creating site legal information"""
    
    # Validate site exists
    site = get_site_by_id(db, legal_data.site_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    # Convert Pydantic model to dict
    legal_dict = legal_data.dict(exclude={'site_id'})
    
    # Create or update site legal info
    legal_info = create_or_update_site_legal_info(db, legal_data.site_id, legal_dict)
    if not legal_info:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create site legal information"
        )
    
    return legal_info


def update_site_legal_info_logic(
    db: Session,
    site_id: uuid.UUID,
    legal_data: SiteLegalInfoUpdate
) -> Dict[str, Any]:
    """Business logic for updating site legal information"""
    
    # Validate site exists
    site = get_site_by_id(db, site_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    # Convert Pydantic model to dict, excluding None values
    update_data = legal_data.dict(exclude_unset=True)
    
    # Create or update site legal info
    legal_info = create_or_update_site_legal_info(db, site_id, update_data)
    if not legal_info:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update site legal information"
        )
    
    return legal_info


def get_legal_statistics_logic(db: Session) -> Dict[str, Any]:
    """Business logic for getting legal statistics"""
    return get_legal_statistics(db)