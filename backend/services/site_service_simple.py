from typing import List, Dict, Any
import uuid

from repositories.site_repository_simple import SiteRepositorySimple
from models import User


class SiteServiceSimple:
    """Service para operaciones simples de sitios - usado principalmente para dropdowns y listas básicas"""
    
    def __init__(self, site_repository: SiteRepositorySimple):
        self.site_repository = site_repository
    
    def get_sites_for_dropdown(self, current_user: User) -> Dict[str, Any]:
        """Obtiene sitios formateados para uso en dropdowns"""
        try:
            sites = self.site_repository.get_sites_for_dropdown()
            return {
                "success": True,
                "sites": sites,
                "total": len(sites)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "sites": []
            }
    
    def get_all_sites_basic(self, current_user: User) -> Dict[str, Any]:
        """Obtiene todos los sitios con información básica"""
        try:
            sites = self.site_repository.get_all_sites_basic()
            
            sites_data = []
            for site in sites:
                sites_data.append({
                    "id": str(site.id),
                    "name": site.name,
                    "code": site.code,
                    "address": site.address,
                    "type": site.site_type,
                    "status": site.status,
                    "latitude": site.latitude,
                    "longitude": site.longitude,
                    "region": site.state,
                    "city": site.city,
                    "description": site.description,
                    "rb_type": site.rb_type,
                    "area_type": site.area_type,
                    "height": site.height,
                    "created_at": site.created_at,
                    "updated_at": site.updated_at
                })
            
            return {
                "success": True,
                "sites": sites_data,
                "total": len(sites_data)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "sites": []
            }
    
    def get_site_detail_basic(self, site_id: uuid.UUID, current_user: User) -> Dict[str, Any]:
        """Obtiene detalles básicos de un sitio"""
        try:
            site = self.site_repository.get_site_by_id(site_id)
            if not site:
                raise ValueError("Sitio no encontrado")
            
            return {
                "success": True,
                "site": {
                    "id": str(site.id),
                    "name": site.name,
                    "code": site.code,
                    "address": site.address,
                    "type": site.site_type,
                    "status": site.status,
                    "latitude": site.latitude,
                    "longitude": site.longitude,
                    "region": site.state,
                    "city": site.city,
                    "country": site.country,
                    "description": site.description,
                    "rb_type": site.rb_type,
                    "area_type": site.area_type,
                    "height": site.height,
                    "created_at": site.created_at,
                    "updated_at": site.updated_at
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_sites_summary(self, current_user: User) -> Dict[str, Any]:
        """Obtiene resumen estadístico de sitios"""
        try:
            summary = self.site_repository.get_sites_summary()
            return {
                "success": True,
                "summary": summary
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "summary": {}
            }
    
    def search_sites(self, search_term: str, current_user: User) -> Dict[str, Any]:
        """Busca sitios por término de búsqueda"""
        try:
            if not search_term or len(search_term.strip()) < 2:
                return {
                    "success": False,
                    "error": "Término de búsqueda debe tener al menos 2 caracteres",
                    "sites": []
                }
            
            sites = self.site_repository.search_sites_by_name(search_term.strip())
            
            sites_data = []
            for site in sites:
                sites_data.append({
                    "id": str(site.id),
                    "name": site.name,
                    "code": site.code,
                    "address": site.address,
                    "type": site.site_type,
                    "status": site.status,
                    "region": site.state
                })
            
            return {
                "success": True,
                "sites": sites_data,
                "total": len(sites_data),
                "search_term": search_term
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "sites": []
            }
    
    def get_sites_by_filters(self, filters: Dict[str, Any], current_user: User) -> Dict[str, Any]:
        """Obtiene sitios aplicando filtros básicos"""
        try:
            sites = []
            
            # Aplicar filtros según los parámetros recibidos
            if filters.get("region"):
                sites = self.site_repository.get_sites_by_region(filters["region"])
            elif filters.get("type"):
                sites = self.site_repository.get_sites_by_type(filters["type"])
            else:
                sites = self.site_repository.get_all_sites_basic()
            
            sites_data = []
            for site in sites:
                sites_data.append({
                    "id": str(site.id),
                    "name": site.name,
                    "code": site.code,
                    "type": site.site_type,
                    "status": site.status,
                    "region": site.state
                })
            
            return {
                "success": True,
                "sites": sites_data,
                "total": len(sites_data),
                "filters_applied": filters
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "sites": []
            }