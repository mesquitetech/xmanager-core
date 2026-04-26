"""
Esquemas Pydantic para la API de Carriers
"""
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from ipaddress import ip_address
from datetime import datetime


class CarrierBase(BaseModel):
    plaza: str
    zona: str
    proveedor: str
    ancho_banda: str
    ip: str
    contacto: str
    email: EmailStr
    telefono: Optional[str] = None
    notas: Optional[str] = None

class CarrierCreate(CarrierBase):
    #created_by: Optional[str] = None
    
    @field_validator('ip')
    @classmethod
    def validate_ip(cls, v):
        try:
            ip_address(v)
        except ValueError:
            raise ValueError("Formato de IP inválido")
        return v

    @field_validator('plaza', 'zona', 'proveedor', 'contacto')
    @classmethod
    def validate_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Este campo es requerido")
        return v.strip()

class CarrierUpdate(BaseModel):
    plaza: Optional[str] = None
    zona: Optional[str] = None
    proveedor: Optional[str] = None
    ancho_banda: Optional[str] = None
    ip: Optional[str] = None
    contacto: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    notas: Optional[str] = None
    updated_by: Optional[str] = None
    
    @field_validator('ip')
    @classmethod
    def validate_ip(cls, v):
        try:
            ip_address(v)
        except ValueError:
            raise ValueError("Formato de IP inválido")
        return v

class CarrierResponse(CarrierBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    class Config:
        from_attributes = True