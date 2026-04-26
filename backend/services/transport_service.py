"""
Transport Service - Lógica de negocio para enlaces de transporte
Parte del patrón de arquitectura limpia: Router → Service → Repository → Database
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from repositories.transport_repository import TransportRepository
from api.transport.schemas import TransportCreate, TransportUpdate, TransportResponse, TransportListResponse
from models.transport import Transport


class TransportService:
    """Service para lógica de negocio de enlaces de transporte"""
    
    def __init__(self, db: Session):
        self.repository = TransportRepository(db)
    
    def create_transport_link(self, transport_data: TransportCreate) -> TransportResponse:
        """Crear un nuevo enlace de transporte con validaciones"""
        
        # Validar duplicado de ID de circuito
        if transport_data.id_circuito:
            self._validate_circuit_id_uniqueness(transport_data.id_circuito)
        
        # Crear enlace de transporte
        transport_dict = transport_data.dict()
        transport_link = self.repository.create(transport_dict)
        
        return TransportResponse.from_orm(transport_link)
    
    def get_transport_links(self, skip: int = 0, limit: int = 100,
                          search: Optional[str] = None,
                          plaza: Optional[str] = None,
                          carrier: Optional[str] = None,
                          estado: Optional[str] = None) -> TransportListResponse:
        """Obtener lista de enlaces con filtros y validaciones"""
        
        # Validar parámetros de paginación
        self._validate_pagination_params(skip, limit)
        
        # Obtener datos del repository
        transport_links, total = self.repository.get_all_with_filters(
            skip=skip,
            limit=limit,
            search=search,
            plaza=plaza,
            carrier=carrier,
            estado=estado
        )
        
        # Convertir a response models
        transport_responses = [TransportResponse.from_orm(link) for link in transport_links]
        
        return TransportListResponse(
            transport_links=transport_responses,
            total=total,
            skip=skip,
            limit=limit
        )
    
    def get_transport_link_by_id(self, transport_id: int) -> TransportResponse:
        """Obtener enlace específico con validación de existencia"""
        
        transport_link = self.repository.get_by_id(transport_id)
        if not transport_link:
            raise HTTPException(
                status_code=404, 
                detail="Enlace de transporte no encontrado"
            )
        
        return TransportResponse.from_orm(transport_link)
    
    def update_transport_link(self, transport_id: int, transport_data: TransportUpdate) -> TransportResponse:
        """Actualizar enlace con validaciones de negocio"""
        
        # Verificar existencia del enlace
        transport_link = self.repository.get_by_id(transport_id)
        if not transport_link:
            raise HTTPException(
                status_code=404, 
                detail="Enlace de transporte no encontrado"
            )
        
        # Validar duplicado de ID de circuito si se está actualizando
        if (transport_data.id_circuito and 
            transport_data.id_circuito != transport_link.id_circuito):
            self._validate_circuit_id_uniqueness_for_update(
                transport_data.id_circuito, 
                transport_id
            )
        
        # Actualizar enlace
        update_dict = transport_data.dict(exclude_unset=True)
        updated_link = self.repository.update(transport_link, update_dict)
        
        return TransportResponse.from_orm(updated_link)
    
    def delete_transport_link(self, transport_id: int) -> dict:
        """Eliminar enlace con validaciones"""
        
        transport_link = self.repository.get_by_id(transport_id)
        if not transport_link:
            raise HTTPException(
                status_code=404, 
                detail="Enlace de transporte no encontrado"
            )
        
        # Validaciones adicionales antes de eliminar (si es necesario)
        self._validate_can_delete(transport_link)
        
        self.repository.delete(transport_link)
        
        return {"message": "Enlace de transporte eliminado exitosamente"}
    
    def get_transport_stats(self) -> dict:
        """Obtener estadísticas con procesamiento adicional"""
        
        stats = self.repository.get_stats()
        
        # Agregar cálculos adicionales de negocio
        if stats["total_links"] > 0:
            stats["utilization_rate"] = round(
                (stats["active_links"] / stats["total_links"]) * 100, 2
            )
            stats["maintenance_rate"] = round(
                (stats["maintenance_links"] / stats["total_links"]) * 100, 2
            )
        else:
            stats["utilization_rate"] = 0.0
            stats["maintenance_rate"] = 0.0
        
        # Agregar status general del sistema
        if stats["utilization_rate"] >= 80:
            stats["system_status"] = "Optimal"
        elif stats["utilization_rate"] >= 60:
            stats["system_status"] = "Good"
        elif stats["utilization_rate"] >= 40:
            stats["system_status"] = "Fair"
        else:
            stats["system_status"] = "Poor"
        
        return stats
    
    # Métodos privados para validaciones
    def _validate_circuit_id_uniqueness(self, circuit_id: str) -> None:
        """Validar que el ID de circuito no exista"""
        existing = self.repository.get_by_circuit_id(circuit_id)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe un enlace con ID de circuito: {circuit_id}"
            )
    
    def _validate_circuit_id_uniqueness_for_update(self, circuit_id: str, exclude_id: int) -> None:
        """Validar unicidad de ID de circuito para actualizaciones"""
        existing = self.repository.get_by_circuit_id_excluding_id(circuit_id, exclude_id)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe otro enlace con ID de circuito: {circuit_id}"
            )
    
    def _validate_pagination_params(self, skip: int, limit: int) -> None:
        """Validar parámetros de paginación"""
        if skip < 0:
            raise HTTPException(
                status_code=400,
                detail="El parámetro 'skip' debe ser mayor o igual a 0"
            )
        
        if limit < 1 or limit > 1000:
            raise HTTPException(
                status_code=400,
                detail="El parámetro 'limit' debe estar entre 1 y 1000"
            )
    
    def _validate_can_delete(self, transport_link: Transport) -> None:
        """Validar si el enlace se puede eliminar"""
        # Aquí se pueden agregar validaciones específicas de negocio
        # Por ejemplo, verificar si el enlace tiene dependencias activas
        
        # Si el enlace está activo, podrías requerir confirmación adicional
        if transport_link.estado == "Activo":
            # En un escenario real, podrías requerir un flag adicional
            # para confirmar la eliminación de enlaces activos
            pass
        
        # Otras validaciones de negocio pueden ir aquí
        pass