from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

from db.database import get_db
from auth.utils import get_current_user
from models import User
from utils.storage import upload_file, create_signed_url, BUCKETS
from . import schemas
from services.inventory_service import (
    get_architecture_connection_logic,
    save_architecture_connection_logic,
    get_infrastructure_logic,
    save_infrastructure_logic,
    get_logical_connection_logic,
    save_logical_connection_logic,
    get_equipment_management_logic,
    save_equipment_management_logic
)

router = APIRouter()

# Architecture Connection endpoints
@router.get("/architecture-connection/{site_id}", response_model=Optional[schemas.ArchitectureConnection])
async def get_architecture_connection(
    site_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get architecture connection data for a specific site"""
    return get_architecture_connection_logic(db, site_id)

@router.post("/architecture-connection", response_model=dict)
async def save_architecture_connection(
    data: schemas.ArchitectureConnectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save architecture connection data"""
    return save_architecture_connection_logic(db, data)

# Infrastructure endpoints
@router.get("/infrastructure/{site_id}", response_model=Optional[schemas.Infrastructure])
async def get_infrastructure(
    site_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get infrastructure data for a specific site"""
    return get_infrastructure_logic(db, site_id)

@router.post("/infrastructure", response_model=dict)
async def save_infrastructure(
    data: schemas.InfrastructureCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save infrastructure data"""
    return save_infrastructure_logic(db, data)

# Logical Connection endpoints
@router.get("/logical-connection/{site_id}", response_model=Optional[schemas.LogicalConnection])
async def get_logical_connection(
    site_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get logical connection data for a specific site"""
    return get_logical_connection_logic(db, site_id)

@router.post("/logical-connection", response_model=dict)
async def save_logical_connection(
    data: schemas.LogicalConnectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save logical connection data"""
    return save_logical_connection_logic(db, data)

# Equipment Management endpoints
@router.get("/equipment-management/{site_id}", response_model=Optional[schemas.EquipmentManagement])
async def get_equipment_management(
    site_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get equipment management data for a specific site"""
    return get_equipment_management_logic(db, site_id)

@router.post("/equipment-management", response_model=dict)
async def save_equipment_management(
    data: schemas.EquipmentManagementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save equipment management data"""
    return save_equipment_management_logic(db, data)

# File upload endpoints
@router.post("/architecture-connection/upload/{site_id}")
async def upload_architecture_file(
    site_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload architecture connection file to Supabase Storage"""
    try:
        file_bytes = await file.read()
        content_type = file.content_type or "application/octet-stream"
        path = upload_file(
            bucket=BUCKETS["arquitectura"],
            file_bytes=file_bytes,
            filename=file.filename,
            content_type=content_type,
            folder=str(site_id),
        )
        signed_url = create_signed_url(BUCKETS["arquitectura"], path)
        return {"filename": file.filename, "url": signed_url, "path": path}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )

@router.get("/architecture-connection/download/{site_id}/{filename}")
async def download_architecture_file(
    site_id: uuid.UUID,
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Redirect to Supabase Storage public URL for download.

    Note: This endpoint is kept for backwards compatibility.
    New uploads return the URL directly from the upload endpoint.
    """
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Use the URL returned by the upload endpoint to access the file directly."
    )