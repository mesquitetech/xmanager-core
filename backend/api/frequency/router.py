from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from models.user import User
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frequency.schemas import FrequencyInventoryCreate, FrequencyInventoryUpdate, FrequencyInventoryResponse
from services.frequency_service import get_frequencies_by_site
from db.session import get_db
from models import SiteFrequencyInventory
from auth.jwt_handler import get_current_user
import uuid

router = APIRouter()


@router.get("/site/{site_id}", response_model=List[FrequencyInventoryResponse])
async def get_site_frequencies(
    site_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all frequency inventory for a specific site"""
    return get_frequencies_by_site(db, site_id)


@router.post("/", response_model=FrequencyInventoryResponse)
async def create_frequency(
    frequency_data: FrequencyInventoryCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new frequency inventory entry"""
    
    # Create new frequency entry
    db_frequency = SiteFrequencyInventory(**frequency_data.dict())
    db.add(db_frequency)
    db.commit()
    db.refresh(db_frequency)
    
    return db_frequency

@router.put("/{frequency_id}", response_model=FrequencyInventoryResponse)
async def update_frequency(
    frequency_id: uuid.UUID,
    frequency_data: FrequencyInventoryUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a frequency inventory entry"""
    
    # Get frequency entry
    db_frequency = db.query(SiteFrequencyInventory).filter(
        SiteFrequencyInventory.id == frequency_id
    ).first()
    
    if not db_frequency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Frequency entry not found"
        )
    
    # Update frequency entry
    update_data = frequency_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_frequency, field, value)
    
    db.commit()
    db.refresh(db_frequency)
    
    return db_frequency

@router.delete("/{frequency_id}")
async def delete_frequency(
    frequency_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a frequency inventory entry"""
    
    # Get frequency entry
    db_frequency = db.query(SiteFrequencyInventory).filter(
        SiteFrequencyInventory.id == frequency_id
    ).first()
    
    if not db_frequency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Frequency entry not found"
        )
    
    db.delete(db_frequency)
    db.commit()
    
    return {"message": "Frequency entry deleted successfully"}

@router.post("/bulk/", response_model=List[FrequencyInventoryResponse])
async def create_bulk_frequencies(
    frequencies_data: List[FrequencyInventoryCreate],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create multiple frequency inventory entries"""
    
    db_frequencies = []
    for frequency_data in frequencies_data:
        db_frequency = SiteFrequencyInventory(**frequency_data.dict())
        db.add(db_frequency)
        db_frequencies.append(db_frequency)
    
    db.commit()
    
    for db_frequency in db_frequencies:
        db.refresh(db_frequency)
    
    return db_frequencies