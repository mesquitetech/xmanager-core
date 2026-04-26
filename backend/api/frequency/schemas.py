from typing import Optional
from datetime import date
from pydantic import BaseModel
import uuid

class FrequencyInventoryCreate(BaseModel):
  site_id: uuid.UUID
  plaza: Optional[str] = None
  ip_gestion: Optional[str] = None
  dispositivo: Optional[str] = None
  frecuencia_1: Optional[str] = None
  frecuencia_2: Optional[str] = None
  banda: Optional[str] = None
  ssid: Optional[str] = None
  estado: Optional[str] = "Activa"
  fecha_instalacion: Optional[date] = None
  fecha_retiro: Optional[date] = None

class FrequencyInventoryUpdate(BaseModel):
  plaza: Optional[str] = None
  ip_gestion: Optional[str] = None
  dispositivo: Optional[str] = None
  frecuencia_1: Optional[str] = None
  frecuencia_2: Optional[str] = None
  banda: Optional[str] = None
  ssid: Optional[str] = None
  estado: Optional[str] = None
  fecha_instalacion: Optional[date] = None
  fecha_retiro: Optional[date] = None

class FrequencyInventoryResponse(BaseModel):
  id: uuid.UUID
  site_id: uuid.UUID
  plaza: Optional[str]
  ip_gestion: Optional[str]
  dispositivo: Optional[str]
  frecuencia_1: Optional[str]
  frecuencia_2: Optional[str]
  banda: Optional[str]
  ssid: Optional[str]
  estado: Optional[str]
  fecha_instalacion: Optional[date]
  fecha_retiro: Optional[date]
  created_at: Optional[str]
  updated_at: Optional[str]

  class Config:
      from_attributes = True