"""
Esquemas Pydantic para el módulo de seguros
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID

class SeguroBase(BaseModel):
    site_id: UUID
    aseguradora: str = Field(..., min_length=1, max_length=255)
    contacto_aseguradora: Optional[str] = Field(None, max_length=255)
    numero_poliza: Optional[str] = Field(None, max_length=100)
    tipo_seguro: Optional[str] = Field(None, max_length=100)
    monto_cubierto: float = Field(..., gt=0)
    cantidad_pagar: float = Field(..., gt=0)
    fecha_pago: date
    frecuencia_pago: str = Field(..., pattern="^(mensual|trimestral|semestral|anual)$")
    fecha_inicio: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    estado: Optional[str] = Field("vigente", pattern="^(vigente|pendiente|vencida|cancelada)$")
    observaciones: Optional[str] = None

class SeguroCreate(SeguroBase):
    pass

class SeguroUpdate(BaseModel):
    aseguradora: Optional[str] = Field(None, min_length=1, max_length=255)
    contacto_aseguradora: Optional[str] = Field(None, max_length=255)
    numero_poliza: Optional[str] = Field(None, max_length=100)
    tipo_seguro: Optional[str] = Field(None, max_length=100)
    monto_cubierto: Optional[float] = Field(None, gt=0)
    cantidad_pagar: Optional[float] = Field(None, gt=0)
    fecha_pago: Optional[date] = None
    frecuencia_pago: Optional[str] = Field(None, pattern="^(mensual|trimestral|semestral|anual)$")
    fecha_inicio: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    estado: Optional[str] = Field(None, pattern="^(vigente|pendiente|vencida|cancelada)$")
    observaciones: Optional[str] = None

class SeguroResponse(SeguroBase):
    id: UUID
    site_name: Optional[str] = None
    site_code: Optional[str] = None
    poliza_filename: Optional[str] = None
    contrato_filename: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SeguroStats(BaseModel):
    total_polizas: int
    polizas_vigentes: int
    polizas_pendientes: int
    polizas_vencidas: int

class SeguroFilter(BaseModel):
    search: Optional[str] = None
    estado: Optional[str] = None
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None
    site_id: Optional[UUID] = None