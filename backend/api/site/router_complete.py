from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import ValidationError
from sqlalchemy.orm import Session
import uuid

from db.database import get_db
from models import User
from auth.utils import get_current_user
from repositories.site_repository_complete import SiteRepository
from services.site_service_complete import SiteServiceComplete

router = APIRouter()


def get_site_service(db: Session = Depends(get_db)) -> SiteServiceComplete:
    """Dependency injection para el servicio de sitios"""
    site_repository = SiteRepository(db)
    return SiteServiceComplete(site_repository)


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_site(
    site_data: Dict = Body(...),
    current_user: User = Depends(get_current_user),
    site_service: SiteServiceComplete = Depends(get_site_service)
):
    """Endpoint para crear un nuevo sitio."""
    """Crea un nuevo sitio"""

    try:
        result = site_service.create_site(site_data, current_user)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update/{site_id}")
async def update_site(
    site_id: uuid.UUID,
    site_data: Dict = Body(...),
    current_user: User = Depends(get_current_user),
    site_service: SiteServiceComplete = Depends(get_site_service)
):
    """Endpoint para actualizar un sitio existente."""
  
    try:
        result = site_service.update_site(site_id, site_data, current_user)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_sites(
    current_user: User = Depends(get_current_user),
    site_service: SiteServiceComplete = Depends(get_site_service)
):
    """Endpoint para listar todos los sitios."""
    try:
        result = site_service.get_all_sites(current_user)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detail/{site_id}")
async def get_site_detail(
    site_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    site_service: SiteServiceComplete = Depends(get_site_service)
):
    """Endpoint para obtener los detalles de un sitio específico."""
    try:
        result = site_service.get_site_detail(site_id, current_user)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process-payment/{site_id}")
async def process_payment(
    site_id: uuid.UUID,
    payment_data: Dict = Body(...),
    current_user: User = Depends(get_current_user),
    site_service: SiteServiceComplete = Depends(get_site_service)
):
    """Endpoint para procesar un pago y actualizar la fecha de próximo pago."""
    try:
        result = site_service.process_payment(site_id, payment_data, current_user)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{site_id}", status_code=200)
async def delete_site(
    site_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    site_service: SiteServiceComplete = Depends(get_site_service)
):
    """Endpoint para eliminar un sitio."""
    print(f"ID PARA ELIMINAR SITE--> {site_id}")
    print("b0e3160e-29a8-4de6-a302-6a2fb4354988")
    print("####ROUTER_COMPLETED_DELETED######")
    try:
        # Verificar que el sitio existe
        site_service.get_site_deleted(site_id, current_user)
        
        # Proceder con eliminación (lógica en el servicio)
        return {"message": "Sitio eliminado correctamente", "site_id": str(site_id)}
    except ValidationError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    