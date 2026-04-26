from pydantic import BaseModel, field_validator
from typing import Optional, List
import uuid
from datetime import datetime, date

# Arquitectura de Conexión Física
class ArchitectureConnectionBase(BaseModel):
    tipo: Optional[str] = None
    tipo_infraestructura: Optional[str] = None
    carrier_peering: Optional[str] = None
    tipo_acceso: Optional[str] = None
    capacidad: Optional[str] = None
    ip_direccionamiento: Optional[str] = None
    gw: Optional[str] = None
    bgp: Optional[str] = None
    prefijos_anunciados: Optional[str] = None

class ArchitectureConnectionCreate(ArchitectureConnectionBase):
    site_id: uuid.UUID

class ArchitectureConnection(ArchitectureConnectionBase):
    id: uuid.UUID
    site_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Infraestructura
class InfrastructureBase(BaseModel):
    tipo_gabinete: Optional[str] = None
    modelo_marca: Optional[str] = None
    enfriamiento: Optional[str] = None
    tipo_enfriamiento: Optional[str] = None
    altura_construccion: Optional[str] = None
    altura_torre: Optional[str] = None
    altura_total: Optional[str] = None
    tipo: Optional[str] = None
    terreno: Optional[str] = None
    acceso: Optional[str] = None
    contacto1: Optional[str] = None
    contacto2: Optional[str] = None
    coordenadas: Optional[str] = None
    sistema_tierras: Optional[str] = None
    luces_obstruccion: Optional[str] = None
    contrato: Optional[str] = None

class InfrastructureCreate(InfrastructureBase):
    site_id: uuid.UUID

class Infrastructure(InfrastructureBase):
    id: uuid.UUID
    site_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Conexión Eléctrica
class ElectricalConnectionBase(BaseModel):
    tipo_corriente: Optional[str] = None
    sistema_respaldo: Optional[str] = None
    baterias_ctd: Optional[int] = None
    duracion_respaldo: Optional[str] = None
    medio_conexion_pop: Optional[str] = None
    contrato_cfe: Optional[str] = None
    no_servicio: Optional[str] = None
    gestion_gabinete: Optional[str] = None

    @field_validator('baterias_ctd', mode='before')
    @classmethod
    def validate_baterias_ctd(cls, v):
        if v == "" or v is None:
            return None
        try:
            return int(v)
        except (ValueError, TypeError):
            return None

class ElectricalConnectionCreate(ElectricalConnectionBase):
    site_id: uuid.UUID

class ElectricalConnection(ElectricalConnectionBase):
    id: uuid.UUID
    site_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Datos Microonda
class MicrowaveDataBase(BaseModel):
    transporte_gestion: Optional[str] = None
    rb_dependiente: Optional[str] = None
    direccionamiento_ip_clientes: Optional[str] = None
    tecnologia_transporte: Optional[str] = None
    tecnologia_clientes: Optional[str] = None
    total_servicios_ptp: Optional[int] = 0
    total_servicios_ptmp: Optional[int] = 0

class MicrowaveDataCreate(MicrowaveDataBase):
    site_id: uuid.UUID

class MicrowaveData(MicrowaveDataBase):
    id: uuid.UUID
    site_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Conexión Lógica
class LogicalConnectionBase(BaseModel):
    direccionamiento_clientes: Optional[str] = None
    direccionamiento_publico: Optional[str] = None

class LogicalConnectionCreate(LogicalConnectionBase):
    site_id: uuid.UUID

class LogicalConnection(LogicalConnectionBase):
    id: uuid.UUID
    site_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Gestión de Equipos
class EquipmentManagementBase(BaseModel):
    core_info: Optional[str] = None
    switch_info: Optional[str] = None
    sensor_luz: Optional[str] = None
    watchdog_info: Optional[str] = None

class EquipmentManagementCreate(EquipmentManagementBase):
    site_id: uuid.UUID

class EquipmentManagement(EquipmentManagementBase):
    id: uuid.UUID
    site_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# PTMP Coverage
class PTMPSector(BaseModel):
    ap: str
    clientes: int = 0

class PTMPCoverageBase(BaseModel):
    sectors: List[PTMPSector] = []

class PTMPCoverageCreate(PTMPCoverageBase):
    site_id: uuid.UUID

class PTMPCoverage(PTMPCoverageBase):
    id: uuid.UUID
    site_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Equipment Registration Schemas
class EquipmentItem(BaseModel):
    nombre: str
    cantidad: int
    watts: float
    id: Optional[int] = None

class EquipmentRegisterBase(BaseModel):
    equipos: List[EquipmentItem]

class EquipmentRegisterCreate(EquipmentRegisterBase):
    site_id: uuid.UUID

class EquipmentRegister(EquipmentRegisterBase):
    site_id: uuid.UUID

    class Config:
        from_attributes = True

# Power Consumption Schemas
class PowerConsumptionData(BaseModel):
    fecha_actualizacion: Optional[str] = None
    sistema_respaldo: Optional[str] = None
    modelo_baterias: Optional[str] = None
    cantidad_baterias: Optional[str] = None
    amhr: Optional[str] = None
    voltaje_operacion: Optional[str] = None
    costo_kw: Optional[str] = None
    costos_fijos: Optional[str] = None
    # Mapped fields for database
    consumo_total_kw: Optional[float] = None
    consumo_pico_kw: Optional[float] = None
    consumo_base_kw: Optional[float] = None
    factor_potencia: Optional[float] = None
    horas_operacion_dia: Optional[int] = None
    costo_kwh_mxn: Optional[float] = None
    consumo_ac_kw: Optional[float] = None
    consumo_telecom_kw: Optional[float] = None

class PowerConsumptionSummary(BaseModel):
    total_watts: float
    total_amperes: float
    total_equipos: int

class PowerConsumptionCreate(BaseModel):
    site_id: uuid.UUID
    datos_generales: PowerConsumptionData
    equipos: List[EquipmentItem]
    resumen: PowerConsumptionSummary

# Anexos PDF
class AnexosPDFBase(BaseModel):
    nombre: str
    categoria: str = "Técnico"
    descripcion: Optional[str] = None

class AnexosPDFCreate(AnexosPDFBase):
    site_id: uuid.UUID
    archivo_nombre: str
    archivo_path: str
    archivo_size: int
    mime_type: str = "application/pdf"
    subido_por: Optional[uuid.UUID] = None

class AnexosPDF(AnexosPDFBase):
    id: uuid.UUID
    site_id: uuid.UUID
    archivo_nombre: str
    archivo_size: int
    fecha_subida: datetime
    subido_por: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True