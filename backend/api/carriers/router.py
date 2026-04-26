"""
API Router para gestión de Carriers (Proveedores)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from db.database import get_db
from models import  User
from auth.utils import get_current_user
from api.carriers.schemas import CarrierCreate
from services.carrier_service import get_carriers_logic, create_carrier_logic, delete_carrier_logic


router = APIRouter(prefix="/carriers", tags=["carriers"])

# Endpoints para carriers
@router.get("/", response_model=List[Dict[str, Any]])
async def get_carriers(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtener lista de carriers con filtros opcionales
    """
    return get_carriers_logic(db, skip, limit, search)


@router.post("/")
async def create_carrier(
    carrier_data: CarrierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crear un nuevo carrier
    """
    return create_carrier_logic(db, carrier_data, current_user.email)


@router.delete("/{carrier_id}")
async def delete_carrier(
    carrier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Eliminar un carrier
    """
    delete_carrier_logic(db, carrier_id)
    return {"message": "Carrier eliminado exitosamente"}