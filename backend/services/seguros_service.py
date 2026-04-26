"""
Service para seguros - Solo lógica de negocio y transformaciones
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date
from uuid import UUID

from repositories.seguros_repository import SegurosRepository
from api.seguros.schemas import SeguroStats, SeguroResponse, SeguroCreate, SeguroUpdate


class SegurosService:
    
    @staticmethod
    def get_stats(db: Session) -> SeguroStats:
        """Obtener estadísticas de seguros con lógica de negocio"""
        stats_data = SegurosRepository.get_seguros_stats(db)
        
        return SeguroStats(
            total_polizas=stats_data["total_polizas"],
            polizas_vigentes=stats_data["polizas_vigentes"],
            polizas_pendientes=stats_data["polizas_pendientes"],
            polizas_vencidas=stats_data["polizas_vencidas"]
        )
    
    @staticmethod
    def get_seguros_list(
        db: Session,
        search: Optional[str] = None,
        estado: Optional[str] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        site_id: Optional[str] = None
    ) -> List[SeguroResponse]:
        """Obtener lista de seguros con transformación de datos"""
        
        # Obtener datos del repository
        seguros = SegurosRepository.get_seguros_filtered(
            db=db,
            search=search,
            estado=estado,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            site_id=site_id
        )
        
        # Transformar a response con lógica de negocio
        response_data = []
        for seguro in seguros:
            seguro_response = SeguroResponse(
                id=seguro.id,
                site_id=seguro.site_id,
                site_name=seguro.site.name if seguro.site else "Sin sitio",
                site_code=seguro.site.code if seguro.site else "N/A",
                aseguradora=seguro.aseguradora,
                contacto_aseguradora=seguro.contacto_aseguradora,
                numero_poliza=seguro.numero_poliza,
                tipo_seguro=seguro.tipo_seguro,
                monto_cubierto=seguro.monto_cubierto,
                cantidad_pagar=seguro.cantidad_pagar,
                fecha_pago=seguro.fecha_pago,
                frecuencia_pago=seguro.frecuencia_pago,
                fecha_inicio=seguro.fecha_inicio,
                fecha_vencimiento=seguro.fecha_vencimiento,
                estado=seguro.estado,
                observaciones=seguro.observaciones,
                created_at=seguro.created_at,
                updated_at=seguro.updated_at,
                # Campos calculados con lógica de negocio
                tiene_documentos=bool(seguro.poliza_filename or seguro.contrato_filename),
                dias_para_vencimiento=SegurosService._calculate_days_to_expiration(seguro.fecha_vencimiento)
            )
            response_data.append(seguro_response)
        
        return response_data
    
    @staticmethod
    def get_seguro_by_id(db: Session, seguro_id: UUID) -> Optional[SeguroResponse]:
        """Obtener un seguro por ID con transformación"""
        seguro = SegurosRepository.get_seguro_by_id(db, seguro_id)
        
        if not seguro:
            return None
        
        return SeguroResponse(
            id=seguro.id,
            site_id=seguro.site_id,
            site_name=seguro.site.name if seguro.site else "Sin sitio",
            site_code=seguro.site.code if seguro.site else "N/A",
            aseguradora=seguro.aseguradora,
            contacto_aseguradora=seguro.contacto_aseguradora,
            numero_poliza=seguro.numero_poliza,
            tipo_seguro=seguro.tipo_seguro,
            monto_cubierto=seguro.monto_cubierto,
            cantidad_pagar=seguro.cantidad_pagar,
            fecha_pago=seguro.fecha_pago,
            frecuencia_pago=seguro.frecuencia_pago,
            fecha_inicio=seguro.fecha_inicio,
            fecha_vencimiento=seguro.fecha_vencimiento,
            estado=seguro.estado,
            observaciones=seguro.observaciones,
            created_at=seguro.created_at,
            updated_at=seguro.updated_at,
            tiene_documentos=bool(seguro.poliza_filename or seguro.contrato_filename),
            dias_para_vencimiento=SegurosService._calculate_days_to_expiration(seguro.fecha_vencimiento)
        )
    
    @staticmethod
    def create_seguro(db: Session, seguro_data: SeguroCreate) -> SeguroResponse:
        """Crear seguro con validaciones de negocio"""
        
        # Validaciones de negocio
        SegurosService._validate_seguro_data(seguro_data)
        
        # Convertir a dict para repository
        create_data = seguro_data.model_dump()
        
        # Crear en repository
        seguro = SegurosRepository.create_seguro(db, create_data)
        
        # Retornar response transformado
        return SegurosService.get_seguro_by_id(db, seguro.id)
    
    @staticmethod
    def update_seguro(db: Session, seguro_id: UUID, update_data: SeguroUpdate) -> Optional[SeguroResponse]:
        """Actualizar seguro con validaciones"""
        
        # Obtener seguro existente
        seguro = SegurosRepository.get_seguro_by_id(db, seguro_id)
        if not seguro:
            return None
        
        # Validaciones de negocio
        SegurosService._validate_update_data(update_data)
        
        # Actualizar en repository
        update_dict = update_data.model_dump(exclude_unset=True)
        updated_seguro = SegurosRepository.update_seguro(db, seguro, update_dict)
        
        # Retornar response transformado
        return SegurosService.get_seguro_by_id(db, updated_seguro.id)
    
    @staticmethod
    def delete_seguro(db: Session, seguro_id: UUID) -> bool:
        """Eliminar seguro con validaciones"""
        
        seguro = SegurosRepository.get_seguro_by_id(db, seguro_id)
        if not seguro:
            return False
        
        # Validaciones de negocio antes de eliminar
        SegurosService._validate_deletion(seguro)
        
        return SegurosRepository.delete_seguro(db, seguro)
    
    @staticmethod
    def _calculate_days_to_expiration(fecha_vencimiento: Optional[date]) -> Optional[int]:
        """Calcular días hasta vencimiento - lógica de negocio"""
        if not fecha_vencimiento:
            return None
        
        today = date.today()
        return (fecha_vencimiento - today).days
    
    @staticmethod
    def _validate_seguro_data(seguro_data: SeguroCreate) -> None:
        """Validaciones de negocio para creación"""
        if seguro_data.monto_cubierto <= 0:
            raise ValueError("El monto cubierto debe ser mayor que 0")
        
        if seguro_data.cantidad_pagar <= 0:
            raise ValueError("La cantidad a pagar debe ser mayor que 0")
        
        if seguro_data.fecha_vencimiento and seguro_data.fecha_inicio:
            if seguro_data.fecha_vencimiento <= seguro_data.fecha_inicio:
                raise ValueError("La fecha de vencimiento debe ser posterior a la fecha de inicio")
    
    @staticmethod
    def _validate_update_data(update_data: SeguroUpdate) -> None:
        """Validaciones de negocio para actualización"""
        if hasattr(update_data, 'monto_cubierto') and update_data.monto_cubierto is not None:
            if update_data.monto_cubierto <= 0:
                raise ValueError("El monto cubierto debe ser mayor que 0")
        
        if hasattr(update_data, 'cantidad_pagar') and update_data.cantidad_pagar is not None:
            if update_data.cantidad_pagar <= 0:
                raise ValueError("La cantidad a pagar debe ser mayor que 0")
    
    @staticmethod
    def _validate_deletion(seguro) -> None:
        """Validaciones antes de eliminar"""
        if seguro.estado == 'vigente':
            raise ValueError("No se puede eliminar un seguro vigente")