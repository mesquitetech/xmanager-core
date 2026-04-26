"""
Router para API de gestión de enlaces de transporte
Implementación de arquitectura limpia: Router → Service → Repository → Database
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from db.database import get_db
from api.transport.schemas import (
    TransportCreate, 
    TransportUpdate, 
    TransportResponse, 
    TransportListResponse
)
from auth.utils import get_current_user
from models import User
from services.transport_service import TransportService

router = APIRouter()


@router.post("/", response_model=TransportResponse)
async def create_transport_link(
    transport_data: TransportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear un nuevo enlace de transporte"""
    service = TransportService(db)
    return service.create_transport_link(transport_data)


@router.get("/", response_model=TransportListResponse)
async def get_transport_links(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    plaza: Optional[str] = Query(None),
    carrier: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener lista de enlaces de transporte con filtros opcionales"""
    service = TransportService(db)
    return service.get_transport_links(skip, limit, search, plaza, carrier, estado)


@router.get("/{transport_id}", response_model=TransportResponse)
async def get_transport_link(
    transport_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener un enlace de transporte específico"""
    service = TransportService(db)
    return service.get_transport_link_by_id(transport_id)


@router.put("/{transport_id}", response_model=TransportResponse)
async def update_transport_link(
    transport_id: int,
    transport_data: TransportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar un enlace de transporte"""
    service = TransportService(db)
    return service.update_transport_link(transport_id, transport_data)


@router.delete("/{transport_id}")
async def delete_transport_link(
    transport_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar un enlace de transporte"""
    service = TransportService(db)
    return service.delete_transport_link(transport_id)


@router.get("/stats/summary")
async def get_transport_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener estadísticas resumidas de enlaces de transporte"""
    service = TransportService(db)
    return service.get_transport_stats()