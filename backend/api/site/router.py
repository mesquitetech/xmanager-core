from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
import uuid

from db.database import get_db
from models import User
from auth.utils import get_current_user
from repositories.site_repository import SiteRepository
from services.site_service import SiteService
router = APIRouter()


def get_site_service(db: Session = Depends(get_db)) -> SiteService:
    """Dependency injection para el servicio principal de sitios"""
    site_repository = SiteRepository(db)
    return SiteService(site_repository)


@router.get("/simple")
async def get_sites_simple(
    current_user: User = Depends(get_current_user),
    site_service: SiteService = Depends(get_site_service)
):
    """Obtiene lista simple de sitios para dropdowns e inventarios"""
    try:
        result = site_service.get_all_sites(current_user, per_page=1000)
        if result["success"]:
            # Formatear para dropdown
            sites_dropdown = [
                {
                    "id": site["id"],
                    "name": site["name"],
                    "code": site["code"],
                    "display_name": f"{site['code']} - {site['name']}" if site.get('code') else site["name"]
                }
                for site in result["sites"]
            ]
            return sites_dropdown
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_sites(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    site_service: SiteService = Depends(get_site_service)
):
    """Obtiene todos los sitios con paginación y filtros"""
    try:
        # Preparar filtros
        filters = {}
        if type:
            filters['site_type'] = type
        if status:
            filters['status'] = status
        
        # Si hay búsqueda, usar función de búsqueda; sino, obtener todos
        if search:
            result = site_service.search_sites(search, filters, current_user)
            if not result["success"]:
                raise HTTPException(status_code=400, detail=result["error"])
                
            # Para búsquedas, aplicar paginación manual
            sites_data = result["sites"]
            total_items = len(sites_data)
            start_idx = (page - 1) * size
            end_idx = start_idx + size
            paginated_sites = sites_data[start_idx:end_idx]
        else:
            result = site_service.get_all_sites(current_user, page, size)
            if not result["success"]:
                raise HTTPException(status_code=500, detail=result["error"])
                
            paginated_sites = result["sites"]
            total_items = result["pagination"]["total"]
        
        # Calcular páginas totales
        total_pages = (total_items + size - 1) // size
        
        return {
            "items": paginated_sites,
            "total_items": total_items,
            "total_pages": total_pages,
            "current_page": page,
            "page_size": size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{site_id}")
async def get_site(
    site_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    site_service: SiteService = Depends(get_site_service)
):
    """Obtiene los detalles de un sitio específico"""
    try:
        result = site_service.get_site_detail(site_id, current_user)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_site(
    site_data: Dict = Body(...),
    current_user: User = Depends(get_current_user),
    site_service: SiteService = Depends(get_site_service)
):
    """Crea un nuevo sitio"""
    print("##################################")
    print(site_data)
    try:
        result = site_service.create_site(site_data, current_user)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{site_id}")
async def update_site(
    site_id: uuid.UUID,
    site_data: Dict = Body(...),
    current_user: User = Depends(get_current_user),
    site_service: SiteService = Depends(get_site_service)
):
    """Actualiza un sitio existente"""
    try:
        result = site_service.update_site(site_id, site_data, current_user)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{site_id}")
async def delete_site(
    site_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    site_service: SiteService = Depends(get_site_service)
):
    """Elimina un sitio"""
    try:
        result = site_service.delete_site(site_id, current_user)
        return {"message": result["message"], "site_id": result["site_id"]}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/summary")
async def get_sites_statistics(
    current_user: User = Depends(get_current_user),
    site_service: SiteService = Depends(get_site_service)
):
    """Obtiene estadísticas de sitios"""
    try:
        result = site_service.get_sites_statistics(current_user)
        if result["success"]:
            return result["statistics"]
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{site_id}/process-payment")
async def process_payment(
    site_id: uuid.UUID,
    payment_data: Dict = Body(...),
    current_user: User = Depends(get_current_user),
    site_service: SiteService = Depends(get_site_service)
):
    """Procesa un pago y actualiza la fecha de próximo pago"""
    try:
        result = site_service.process_payment(site_id, payment_data, current_user)
        return {"message": result["message"], "site_id": result["site_id"]}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/{search_term}")
async def search_sites(
    search_term: str,
    type: Optional[str] = None,
    status: Optional[str] = None,
    region: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    site_service: SiteService = Depends(get_site_service)
):
    """Busca sitios por término de búsqueda y filtros"""
    try:
        filters = {}
        if type:
            filters['site_type'] = type
        if status:
            filters['status'] = status
        if region:
            filters['region'] = region
            
        result = site_service.search_sites(search_term, filters, current_user)
        if result["success"]:
            return {
                "sites": result["sites"],
                "total": result["total"],
                "search_term": result["search_term"],
                "filters": result["filters"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))