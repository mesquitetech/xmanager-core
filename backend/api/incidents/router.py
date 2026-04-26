from typing import Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
import uuid

from db.database import get_db
from models import User, UserRole, IncidentStatus, IncidentPriority
from auth.utils import get_current_user, check_role
from . import schemas
from services.incident_service import (
    get_incidents_logic,
    get_incident_logic,
    create_incident_logic,
    update_incident_logic,
    delete_incident_logic,
    assign_incident_logic
)

router = APIRouter()

# Get all incidents with pagination
@router.get("/", response_model=schemas.IncidentList)
async def get_incidents(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    site_id: Optional[uuid.UUID] = None,
    status: Optional[IncidentStatus] = None,
    priority: Optional[IncidentPriority] = None,
    category: Optional[str] = None,
    assignee_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get incidents with filters and pagination"""
    return get_incidents_logic(db, skip, limit, site_id, status, priority, category, assignee_id)

# Get incident by ID
@router.get("/{incident_id}", response_model=schemas.Incident)
async def get_incident(
    incident_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get single incident by ID"""
    return get_incident_logic(db, incident_id)

# Create new incident
@router.post("/", response_model=schemas.Incident, status_code=status.HTTP_201_CREATED)
async def create_incident(
    incident_data: schemas.IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new incident"""
    return create_incident_logic(db, incident_data, current_user)

# Update incident
@router.put("/{incident_id}", response_model=schemas.Incident)
async def update_incident(
    incident_id: uuid.UUID,
    incident_data: schemas.IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update incident"""
    return update_incident_logic(db, incident_id, incident_data, current_user)

# Delete incident
@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_incident(
    incident_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_role([UserRole.ADMINISTRADOR, UserRole.OPERATIVO]))
):
    """Delete incident"""
    return delete_incident_logic(db, incident_id)

# Assign incident
@router.put("/{incident_id}/assign", response_model=schemas.Incident)
async def assign_incident(
    incident_id: uuid.UUID,
    assignee_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_role([UserRole.ADMINISTRADOR, UserRole.OPERATIVO]))
):
    """Assign incident to user"""
    return assign_incident_logic(db, incident_id, assignee_id)