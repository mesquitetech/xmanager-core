"""
Transport Repository - Manejo de operaciones de base de datos para enlaces de transporte
Parte del patrón de arquitectura limpia: Router → Service → Repository → Database
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from typing import Optional, List, Tuple
from models.transport import Transport


class TransportRepository:
    """Repository para operaciones de base de datos de enlaces de transporte"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, transport_data: dict) -> Transport:
        """Crear un nuevo enlace de transporte"""
        transport_link = Transport(**transport_data)
        self.db.add(transport_link)
        self.db.commit()
        self.db.refresh(transport_link)
        return transport_link
    
    def get_by_id(self, transport_id: int) -> Optional[Transport]:
        """Obtener enlace de transporte por ID"""
        return self.db.query(Transport).filter(Transport.id == transport_id).first()
    
    def get_by_circuit_id(self, circuit_id: str) -> Optional[Transport]:
        """Obtener enlace de transporte por ID de circuito"""
        return self.db.query(Transport).filter(Transport.id_circuito == circuit_id).first()
    
    def get_by_circuit_id_excluding_id(self, circuit_id: str, exclude_id: int) -> Optional[Transport]:
        """Obtener enlace por ID de circuito excluyendo un ID específico (para validar duplicados en updates)"""
        return self.db.query(Transport).filter(
            and_(
                Transport.id_circuito == circuit_id,
                Transport.id != exclude_id
            )
        ).first()
    
    def get_all_with_filters(self, skip: int = 0, limit: int = 100, 
                           search: Optional[str] = None,
                           plaza: Optional[str] = None,
                           carrier: Optional[str] = None,
                           estado: Optional[str] = None) -> Tuple[List[Transport], int]:
        """Obtener lista de enlaces con filtros y paginación"""
        query = self.db.query(Transport)
        
        # Aplicar filtros
        if search:
            search_filter = or_(
                Transport.plaza.ilike(f"%{search}%"),
                Transport.enlace.ilike(f"%{search}%"),
                Transport.carrier.ilike(f"%{search}%"),
                Transport.id_circuito.ilike(f"%{search}%"),
                Transport.contacto.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if plaza:
            query = query.filter(Transport.plaza.ilike(f"%{plaza}%"))
        
        if carrier:
            query = query.filter(Transport.carrier.ilike(f"%{carrier}%"))
        
        if estado:
            query = query.filter(Transport.estado == estado)
        
        # Contar total antes de paginación
        total = query.count()
        
        # Aplicar paginación y ordenamiento
        transport_links = query.order_by(desc(Transport.updated_at)).offset(skip).limit(limit).all()
        
        return transport_links, total
    
    def update(self, transport_link: Transport, update_data: dict) -> Transport:
        """Actualizar enlace de transporte"""
        for field, value in update_data.items():
            setattr(transport_link, field, value)
        
        self.db.commit()
        self.db.refresh(transport_link)
        return transport_link
    
    def delete(self, transport_link: Transport) -> None:
        """Eliminar enlace de transporte"""
        self.db.delete(transport_link)
        self.db.commit()
    
    def get_stats(self) -> dict:
        """Obtener estadísticas de enlaces de transporte"""
        total_links = self.db.query(Transport).count()
        active_links = self.db.query(Transport).filter(Transport.estado == "Activo").count()
        inactive_links = self.db.query(Transport).filter(Transport.estado == "Inactivo").count()
        maintenance_links = self.db.query(Transport).filter(Transport.estado == "Mantenimiento").count()
        
        # Obtener carriers únicos
        carriers = self.db.query(Transport.carrier).distinct().all()
        carrier_list = [c[0] for c in carriers if c[0]]
        
        # Obtener plazas únicas
        plazas = self.db.query(Transport.plaza).distinct().all()
        plaza_list = [p[0] for p in plazas if p[0]]
        
        return {
            "total_links": total_links,
            "active_links": active_links,
            "inactive_links": inactive_links,
            "maintenance_links": maintenance_links,
            "total_carriers": len(carrier_list),
            "total_plazas": len(plaza_list),
            "carriers": carrier_list,
            "plazas": plaza_list
        }