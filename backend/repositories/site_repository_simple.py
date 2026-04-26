from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid

from models import Site


class SiteRepositorySimple:
    """Repository para operaciones simples de sitios - usado principalmente para dropdowns y listas básicas"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_sites_basic(self) -> List[Site]:
        """Obtiene todos los sitios con información básica para dropdowns"""
        return self.db.query(Site).all()
    
    def get_sites_for_dropdown(self) -> List[Dict[str, Any]]:
        """Obtiene sitios formateados para uso en dropdowns"""
        sites = self.db.query(Site.id, Site.name, Site.code).all()
        return [
            {
                "id": str(site.id),
                "name": site.name,
                "code": site.code,
                "display": f"{site.code} - {site.name}"
            }
            for site in sites
        ]
    
    def get_site_by_id(self, site_id: uuid.UUID) -> Site:
        """Obtiene un sitio por ID"""
        return self.db.query(Site).filter(Site.id == site_id).first()
    
    def get_sites_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de sitios para estadísticas básicas"""
        total_sites = self.db.query(Site).count()
        active_sites = self.db.query(Site).filter(Site.status == 'ACTIVE').count()
        inactive_sites = self.db.query(Site).filter(Site.status == 'INACTIVE').count()
        
        return {
            "total": total_sites,
            "active": active_sites,
            "inactive": inactive_sites,
            "maintenance": self.db.query(Site).filter(Site.status == 'MAINTENANCE').count()
        }
    
    def search_sites_by_name(self, search_term: str) -> List[Site]:
        """Busca sitios por nombre o código"""
        return self.db.query(Site).filter(
            Site.name.ilike(f"%{search_term}%") | 
            Site.code.ilike(f"%{search_term}%")
        ).all()
    
    def get_sites_by_region(self, region: str) -> List[Site]:
        """Obtiene sitios filtrados por región"""
        return self.db.query(Site).filter(Site.state.ilike(f"%{region}%")).all()
    
    def get_sites_by_type(self, site_type: str) -> List[Site]:
        """Obtiene sitios filtrados por tipo"""
        return self.db.query(Site).filter(Site.site_type == site_type).all()
    
    def commit(self):
        """Confirma cambios en la base de datos"""
        self.db.commit()
    
    def rollback(self):
        """Revierte cambios en la base de datos"""
        self.db.rollback()