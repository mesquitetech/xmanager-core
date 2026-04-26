"""
Repository para seguros - Solo acceso a datos y consultas SQL
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import date
from uuid import UUID

from models import Seguro, Site


class SegurosRepository:
    
    @staticmethod
    def get_seguros_stats(db: Session) -> Dict[str, int]:
        """Obtener estadísticas de seguros desde la base de datos"""
        total_polizas = db.query(Seguro).count()
        polizas_vigentes = db.query(Seguro).filter(Seguro.estado == 'vigente').count()
        polizas_pendientes = db.query(Seguro).filter(Seguro.estado == 'pendiente').count()
        polizas_vencidas = db.query(Seguro).filter(Seguro.estado == 'vencida').count()
        
        return {
            "total_polizas": total_polizas,
            "polizas_vigentes": polizas_vigentes,
            "polizas_pendientes": polizas_pendientes,
            "polizas_vencidas": polizas_vencidas
        }
    
    @staticmethod
    def get_seguros_filtered(
        db: Session,
        search: Optional[str] = None,
        estado: Optional[str] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        site_id: Optional[str] = None
    ) -> List[Seguro]:
        """Obtener seguros con filtros aplicados"""
        query = db.query(Seguro).join(Site, Seguro.site_id == Site.id)
        
        # Aplicar filtros
        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    Site.name.ilike(search_term),
                    Site.code.ilike(search_term),
                    Seguro.aseguradora.ilike(search_term)
                )
            )
        
        if estado:
            query = query.filter(Seguro.estado == estado)
        
        if fecha_desde:
            query = query.filter(Seguro.fecha_pago >= fecha_desde)
        
        if fecha_hasta:
            query = query.filter(Seguro.fecha_pago <= fecha_hasta)
        
        if site_id:
            query = query.filter(Seguro.site_id == site_id)
        
        return query.order_by(Seguro.fecha_pago.desc()).all()
    
    @staticmethod
    def get_seguro_by_id(db: Session, seguro_id: UUID) -> Optional[Seguro]:
        """Obtener un seguro por ID"""
        return db.query(Seguro).filter(Seguro.id == seguro_id).first()
    
    @staticmethod
    def create_seguro(db: Session, seguro_data: Dict[str, Any]) -> Seguro:
        """Crear un nuevo seguro"""
        seguro = Seguro(**seguro_data)
        db.add(seguro)
        db.flush()
        db.refresh(seguro)
        return seguro
    
    @staticmethod
    def update_seguro(db: Session, seguro: Seguro, update_data: Dict[str, Any]) -> Seguro:
        """Actualizar un seguro existente"""
        for field, value in update_data.items():
            if hasattr(seguro, field):
                setattr(seguro, field, value)
        
        db.flush()
        db.refresh(seguro)
        return seguro
    
    @staticmethod
    def delete_seguro(db: Session, seguro: Seguro) -> bool:
        """Eliminar un seguro"""
        db.delete(seguro)
        db.flush()
        return True
    
    @staticmethod
    def get_seguros_by_site(db: Session, site_id: UUID) -> List[Seguro]:
        """Obtener todos los seguros de un sitio específico"""
        return db.query(Seguro).filter(Seguro.site_id == site_id).all()