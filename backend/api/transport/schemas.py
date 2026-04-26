"""
Esquemas Pydantic para API de transporte
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class TransportBase(BaseModel):
    plaza: str = Field(..., min_length=1, max_length=100)
    enlace: str = Field(..., min_length=1, max_length=100)
    carrier: str = Field(..., min_length=1, max_length=100)
    servicio: str = Field(..., min_length=1, max_length=100)
    trafico_actual: Optional[str] = Field(None, max_length=50)
    contacto: str = Field(..., min_length=1, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    telefono: Optional[str] = Field(None, max_length=20)
    id_circuito: Optional[str] = Field(None, max_length=100)
    capacidad_total: Optional[str] = Field(None, max_length=50)
    tipo_enlace: Optional[str] = Field(None, max_length=50)
    estado: Optional[str] = Field("Activo", max_length=20)
    fecha_contrato: Optional[datetime] = None
    fecha_vencimiento: Optional[datetime] = None
    costo_mensual: Optional[float] = None
    notas: Optional[str] = None

    @validator('email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Email debe contener @')
        return v

    @validator('estado')
    def validate_estado(cls, v):
        valid_estados = ['Activo', 'Inactivo', 'Mantenimiento']
        if v and v not in valid_estados:
            raise ValueError(f'Estado debe ser uno de: {valid_estados}')
        return v


class TransportCreate(TransportBase):
    pass


class TransportUpdate(BaseModel):
    plaza: Optional[str] = Field(None, min_length=1, max_length=100)
    enlace: Optional[str] = Field(None, min_length=1, max_length=100)
    carrier: Optional[str] = Field(None, min_length=1, max_length=100)
    servicio: Optional[str] = Field(None, min_length=1, max_length=100)
    trafico_actual: Optional[str] = Field(None, max_length=50)
    contacto: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    telefono: Optional[str] = Field(None, max_length=20)
    id_circuito: Optional[str] = Field(None, max_length=100)
    capacidad_total: Optional[str] = Field(None, max_length=50)
    tipo_enlace: Optional[str] = Field(None, max_length=50)
    estado: Optional[str] = Field(None, max_length=20)
    fecha_contrato: Optional[datetime] = None
    fecha_vencimiento: Optional[datetime] = None
    costo_mensual: Optional[float] = None
    notas: Optional[str] = None


class TransportResponse(TransportBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransportListResponse(BaseModel):
    transport_links: List[TransportResponse]
    total: int
    skip: int
    limit: int