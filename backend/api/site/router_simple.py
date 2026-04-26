from typing import Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from db.database import get_db
from models import User
from auth.utils import get_current_user
from repositories.site_repository_simple import SiteRepositorySimple
from services.site_service_simple import SiteServiceSimple

router = APIRouter()


def get_site_service_simple(db: Session = Depends(get_db)) -> SiteServiceSimple:
    """Dependency injection para el servicio simple de sitios"""
    site_repository = SiteRepositorySimple(db)
    return SiteServiceSimple(site_repository)


@router.get("/")
async def get_all_sites_simple(
    current_user: User = Depends(get_current_user),
    site_service: SiteServiceSimple = Depends(get_site_service_simple)
):
    """Endpoint para obtener todos los sitios - información básica"""
    try:
        result = site_service.get_all_sites_basic(current_user)
        if result["success"]:
            return result["sites"]
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dropdown")
async def get_sites_dropdown(
    current_user: User = Depends(get_current_user),
    site_service: SiteServiceSimple = Depends(get_site_service_simple)
):
    """Endpoint para obtener sitios formateados para dropdowns"""
    try:
        result = site_service.get_sites_for_dropdown(current_user)
        if result["success"]:
            return result["sites"]
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_sites_summary(
    current_user: User = Depends(get_current_user),
    site_service: SiteServiceSimple = Depends(get_site_service_simple)
):
    """Endpoint para obtener resumen estadístico de sitios"""
    try:
        result = site_service.get_sites_summary(current_user)
        if result["success"]:
            return result["summary"]
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/{search_term}")
async def search_sites(
    search_term: str,
    current_user: User = Depends(get_current_user),
    site_service: SiteServiceSimple = Depends(get_site_service_simple)
):
    """Endpoint para buscar sitios por término de búsqueda"""
    try:
        result = site_service.search_sites(search_term, current_user)
        if result["success"]:
            return result["sites"]
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detail/{site_id}")
async def get_site_detail_simple(
    site_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    site_service: SiteServiceSimple = Depends(get_site_service_simple)
):
    """Endpoint para obtener detalles básicos de un sitio"""
    try:
        result = site_service.get_site_detail_basic(site_id, current_user)
        if result["success"]:
            return result["site"]
        else:
            raise HTTPException(status_code=404, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/filter")
async def get_sites_filtered(
    region: str = None,
    site_type: str = None,
    current_user: User = Depends(get_current_user),
    site_service: SiteServiceSimple = Depends(get_site_service_simple)
):
    """Endpoint para obtener sitios filtrados por región o tipo"""
    try:
        filters = {}
        if region:
            filters["region"] = region
        if site_type:
            filters["type"] = site_type
            
        result = site_service.get_sites_by_filters(filters, current_user)
        if result["success"]:
            return result["sites"]
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))