from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
import enum

# Simple site model for dropdowns and selects
class SimpleSite(BaseModel):
    id: str
    name: str

# Base models
class SitePhotoBase(BaseModel):
    photo_url: str
    photo_description: Optional[str] = None
    photo_category: Optional[str] = None
    taken_at: Optional[datetime] = None

class SitePhotoCreate(SitePhotoBase):
    pass

class SitePhoto(SitePhotoBase):
    id: UUID
    site_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class PaymentFrequency(str, enum.Enum):
    SINGLE = "single"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMIANNUAL = "semiannual"
    ANNUAL = "annual"

class SiteLegalInfoBase(BaseModel):
    contract_start_date: Optional[datetime] = None
    contract_end_date: Optional[datetime] = None
    contract_document_path: Optional[str] = None
    monthly_rent: Optional[float] = None
    currency: str = "USD"
    landlord_name: Optional[str] = None
    landlord_contact: Optional[str] = None
    landlord_email: Optional[str] = None
    payment_frequency: Optional[str] = "monthly"
    next_payment_date: Optional[datetime] = None
    notes: Optional[str] = None

class SiteLegalInfoCreate(SiteLegalInfoBase):
    pass

class SiteLegalInfo(SiteLegalInfoBase):
    id: UUID
    site_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SiteNetworkInfoBase(BaseModel):
    network_topology: Optional[Dict[str, Any]] = None
    ip_ranges: Optional[str] = None
    subnet_mask: Optional[str] = None
    gateway: Optional[str] = None
    primary_dns: Optional[str] = None
    secondary_dns: Optional[str] = None
    bandwidth: Optional[str] = None
    isp_provider: Optional[str] = None
    network_diagram_path: Optional[str] = None
    notes: Optional[str] = None

class SiteNetworkInfoCreate(SiteNetworkInfoBase):
    pass

class SiteNetworkInfo(SiteNetworkInfoBase):
    id: UUID
    site_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SiteEnergyInfoBase(BaseModel):
    power_source: Optional[str] = None
    has_generator: bool = False
    generator_details: Optional[Dict[str, Any]] = None
    has_solar: bool = False
    solar_details: Optional[Dict[str, Any]] = None
    has_batteries: bool = False
    battery_details: Optional[Dict[str, Any]] = None
    power_consumption: Optional[float] = None
    utility_provider: Optional[str] = None
    meter_number: Optional[str] = None
    electrical_diagram_path: Optional[str] = None
    notes: Optional[str] = None

class SiteEnergyInfoCreate(SiteEnergyInfoBase):
    pass

class SiteEnergyInfo(SiteEnergyInfoBase):
    id: UUID
    site_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SiteInfrastructureInfoBase(BaseModel):
    tower_type: Optional[str] = None
    tower_height: Optional[float] = None
    tower_manufacturer: Optional[str] = None
    shelter_type: Optional[str] = None
    shelter_dimensions: Optional[str] = None
    security_measures: Optional[Dict[str, Any]] = None
    has_air_conditioning: bool = False
    ac_details: Optional[Dict[str, Any]] = None
    has_fire_protection: bool = False
    fire_protection_details: Optional[Dict[str, Any]] = None
    cable_routes: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class SiteInfrastructureInfoCreate(SiteInfrastructureInfoBase):
    pass

class SiteInfrastructureInfo(SiteInfrastructureInfoBase):
    id: UUID
    site_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SitePaymentBase(BaseModel):
    payment_date: datetime
    amount: float
    currency: str = "USD"
    payment_type: str
    payment_method: Optional[str] = None
    reference_number: Optional[str] = None
    receipt_document_path: Optional[str] = None
    notes: Optional[str] = None

class SitePaymentCreate(SitePaymentBase):
    pass

class SitePayment(SitePaymentBase):
    id: UUID
    site_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class EquipmentBase(BaseModel):
    name: str
    equipment_type: Optional[str] = None
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[datetime] = None
    warranty_end_date: Optional[datetime] = None
    status: Optional[str] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    firmware_version: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    location_in_site: Optional[str] = None
    notes: Optional[str] = None

class EquipmentCreate(EquipmentBase):
    pass

class Equipment(EquipmentBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Main Site models
class SiteBase(BaseModel):
    name: str
    code: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    site_type: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None

class SiteCreate(SiteBase):
    legal_info: Optional[SiteLegalInfoCreate] = None
    network_info: Optional[SiteNetworkInfoCreate] = None
    energy_info: Optional[SiteEnergyInfoCreate] = None
    infrastructure_info: Optional[SiteInfrastructureInfoCreate] = None
    photos: Optional[List[SitePhotoCreate]] = None

class SiteUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    site_type: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    legal_info: Optional[SiteLegalInfoCreate] = None
    network_info: Optional[SiteNetworkInfoCreate] = None
    energy_info: Optional[SiteEnergyInfoCreate] = None
    infrastructure_info: Optional[SiteInfrastructureInfoCreate] = None

class Site(SiteBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    legal_info: Optional[SiteLegalInfo] = None
    network_info: Optional[SiteNetworkInfo] = None
    energy_info: Optional[SiteEnergyInfo] = None
    infrastructure_info: Optional[SiteInfrastructureInfo] = None
    photos: List[SitePhoto] = []
    payments: List[SitePayment] = []
    
    class Config:
        from_attributes = True

class SiteList(BaseModel):
    items: List[Site]
    total_items: int
    current_page: int
    page_size: int
    total_pages: int
