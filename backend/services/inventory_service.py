"""
Service layer for inventory operations
Handles business logic and validation for inventory-related operations
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import uuid

from repositories.inventory_repository import (
    get_architecture_connection_by_site_id,
    create_or_update_architecture_connection,
    get_infrastructure_by_site_id,
    create_or_update_infrastructure,
    get_logical_connection_by_site_id,
    create_or_update_logical_connection,
    get_equipment_management_by_site_id,
    create_or_update_equipment_management,
    get_site_by_id
)
from api.inventory.schemas import (
    ArchitectureConnectionCreate,
    InfrastructureCreate,
    LogicalConnectionCreate,
    EquipmentManagementCreate
)


def get_architecture_connection_logic(db: Session, site_id: uuid.UUID) -> Optional[Dict[str, Any]]:
    """Business logic for getting architecture connection"""
    # Validate site exists
    site = get_site_by_id(db, site_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    return get_architecture_connection_by_site_id(db, site_id)


def save_architecture_connection_logic(
    db: Session,
    data: ArchitectureConnectionCreate
) -> Dict[str, str]:
    """Business logic for saving architecture connection"""
    # Validate site exists
    site = get_site_by_id(db, data.site_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    # Convert Pydantic model to dict
    data_dict = data.dict()
    
    # Save to database
    success = create_or_update_architecture_connection(db, data_dict)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save architecture connection data"
        )
    
    return {"status": "success"}


def get_infrastructure_logic(db: Session, site_id: uuid.UUID) -> Optional[Dict[str, Any]]:
    """Business logic for getting infrastructure"""
    # Validate site exists
    site = get_site_by_id(db, site_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    return get_infrastructure_by_site_id(db, site_id)


def save_infrastructure_logic(db: Session, data: InfrastructureCreate) -> Dict[str, str]:
    """Business logic for saving infrastructure"""
    # Validate site exists
    site = get_site_by_id(db, data.site_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    # Convert Pydantic model to dict
    data_dict = data.dict()
    
    # Save to database
    success = create_or_update_infrastructure(db, data_dict)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save infrastructure data"
        )
    
    return {"status": "success"}


def get_logical_connection_logic(db: Session, site_id: uuid.UUID) -> Optional[Dict[str, Any]]:
    """Business logic for getting logical connection"""
    # Validate site exists
    site = get_site_by_id(db, site_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    return get_logical_connection_by_site_id(db, site_id)


def save_logical_connection_logic(db: Session, data: LogicalConnectionCreate) -> Dict[str, str]:
    """Business logic for saving logical connection"""
    # Validate site exists
    site = get_site_by_id(db, data.site_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    # Convert Pydantic model to dict
    data_dict = data.dict()
    
    # Save to database
    success = create_or_update_logical_connection(db, data_dict)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save logical connection data"
        )
    
    return {"status": "success"}


def get_equipment_management_logic(db: Session, site_id: uuid.UUID) -> Optional[Dict[str, Any]]:
    """Business logic for getting equipment management"""
    # Validate site exists
    site = get_site_by_id(db, site_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    return get_equipment_management_by_site_id(db, site_id)


def save_equipment_management_logic(db: Session, data: EquipmentManagementCreate) -> Dict[str, str]:
    """Business logic for saving equipment management"""
    # Validate site exists
    site = get_site_by_id(db, data.site_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    # Convert Pydantic model to dict
    data_dict = data.dict()
    
    # Save to database
    success = create_or_update_equipment_management(db, data_dict)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save equipment management data"
        )
    
    return {"status": "success"}