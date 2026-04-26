from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid
from datetime import datetime

from models import Site, SiteLegalInfo, PaymentEvidence


class SiteRepository:
    """Repository para manejo de operaciones de base de datos de sitios"""
    
    def __init__(self, db: Session):
        self.db = db
    ######## CODIGO EN CORECION  #########
    def get_all_sites(self) -> List[Site]:
        """Obtiene todos los sitios de la base de datos"""
        # llamar api odoo campos,  
        return self.db.query(Site).all()
    
    def get_site_by_id(self, site_id: uuid.UUID) -> Optional[Site]:
        """Obtiene un sitio por su ID"""
        return self.db.query(Site).filter(Site.id == site_id).first()
    
    def create_site(self, site_data: Dict[str, Any]) -> Site:
        """Crea un nuevo sitio en la base de datos"""
        # Crear punto geométrico si hay coordenadas válidas
        geom = None
        latitude = site_data.get('latitude', 0.0)
        longitude = site_data.get('longitude', 0.0)
        
        if latitude != 0.0 and longitude != 0.0:
            geom = func.ST_SetSRID(
                func.ST_MakePoint(longitude, latitude),
                4326
            )
        
        # Crear nuevo sitio
        new_site = Site(
            name=site_data['name'],
            code=site_data['code'],
            address=site_data.get('address', ''),
            city=site_data.get('city', ''),
            state=site_data.get('state', ''),
            country=site_data.get('country', 'México'),
            zip_code=site_data.get('zip_code', ''),
            latitude=latitude,
            longitude=longitude,
            geom=geom,
            site_type=site_data.get('site_type', 'TOWER'),
            status=site_data.get('status', 'ACTIVE'),
            description=site_data.get('description', ''),
            rb_type=site_data.get('rb_type', ''),
            height=site_data.get('height'),
            area_type=site_data.get('area_type', '')
        )
        
        self.db.add(new_site)
        self.db.flush()  # Para obtener el ID sin commit completo
        return new_site
    
    def update_site(self, site: Site, site_data: Dict[str, Any]) -> Site:
        """Actualiza un sitio existente"""
        # Actualizar campos básicos
        for field in ['name', 'code', 'address', 'city', 'state', 'country', 
                     'zip_code', 'site_type', 'status', 'description', 
                     'rb_type', 'height', 'area_type']:
            if field in site_data:
                setattr(site, field, site_data[field])
        
        # Actualizar coordenadas y geometría
        if 'latitude' in site_data and 'longitude' in site_data:
            latitude = site_data['latitude']
            longitude = site_data['longitude']
            
            site.latitude = latitude
            site.longitude = longitude
            
            # Note: geom update handled by SQLAlchemy relationship
        
        # Note: updated_at handled automatically by SQLAlchemy
        return site
    
    def delete_site(self, site_id: uuid.UUID) -> bool:
        """Elimina un sitio de la base de datos"""
        try:
            site = self.get_site_by_id(site_id)
            print(f"SITE--> {site} en repository complete")
            if site:
                self.db.delete(site)
                self.db.commit()
                return True
            return False
        except Exception:
            self.db.rollback()
            return False
    
    def create_legal_info(self, site_id: uuid.UUID, legal_data: Dict[str, Any]) -> SiteLegalInfo:
        """Crea información legal para un sitio"""
        legal_info = SiteLegalInfo(
            site_id=site_id,
            landlord_name=legal_data.get('landlord_name'),
            landlord_contact=legal_data.get('landlord_contact'),
            landlord_email=legal_data.get('landlord_email'),
            contract_start_date=legal_data.get('contract_start_date'),
            contract_end_date=legal_data.get('contract_end_date'),
            monthly_rent=legal_data.get('monthly_rent'),
            currency=legal_data.get('currency', 'MXN'),
            payment_frequency=legal_data.get('payment_frequency', 'monthly'),
            next_payment_date=legal_data.get('next_payment_date'),
            service_provider=legal_data.get('service_provider'),
            electricity_support=legal_data.get('electricity_support'),
            internet_exchange=legal_data.get('internet_exchange'),
            notes=legal_data.get('notes'),
            period=legal_data.get('period'),
            noc_status=legal_data.get('noc_status'),
            infra_status=legal_data.get('infra_status'),
            network_arch_status=legal_data.get('network_arch_status'),
            classification=legal_data.get('classification'),
            contract_date=legal_data.get('contract_date'),
            requires_invoice=legal_data.get('requires_invoice'),
            courtesy_service=legal_data.get('courtesy_service'),
            courtesy_service_details=legal_data.get('courtesy_service_details'),
            landlord_phone=legal_data.get('landlord_phone')
        )
        
        self.db.add(legal_info)
        return legal_info
    
    def update_legal_info(self, legal_info: SiteLegalInfo, legal_data: Dict[str, Any]) -> SiteLegalInfo:
        """Actualiza información legal de un sitio"""
        for field in ['landlord_name', 'landlord_contact', 'landlord_email',
                     'contract_start_date', 'contract_end_date', 'monthly_rent',
                     'currency', 'payment_frequency', 'next_payment_date',
                     'service_provider', 'electricity_support', 'internet_exchange',
                     'notes', 'period', 'noc_status', 'infra_status',
                     'network_arch_status', 'classification', 'contract_date',
                     'requires_invoice', 'courtesy_service', 'courtesy_service_details',
                     'landlord_phone', 'payment_status', 'payment_evidence_file',
                     'payment_evidence_type']:
            if field in legal_data:
                # Manejar fechas vacías
                if field.endswith('_date') and legal_data[field] == '':
                    setattr(legal_info, field, None)
                else:
                    setattr(legal_info, field, legal_data[field])
        
        return legal_info
    
    def get_payment_evidence_by_site(self, site_id: uuid.UUID) -> List[PaymentEvidence]:
        """Obtiene todas las evidencias de pago de un sitio"""
        return self.db.query(PaymentEvidence).filter(
            PaymentEvidence.site_id == site_id
        ).all()
    
    def create_payment_evidence(self, evidence_data: Dict[str, Any]) -> PaymentEvidence:
        """Crea una nueva evidencia de pago"""
        evidence = PaymentEvidence(
            site_id=evidence_data['site_id'],
            file_name=evidence_data['file_name'],
            file_data=evidence_data['file_data'],
            uploaded_by_id=evidence_data['uploaded_by_id']
        )
        
        self.db.add(evidence)
        return evidence
    
    def update_payment_evidence(self, evidence: PaymentEvidence, evidence_data: Dict[str, Any]) -> PaymentEvidence:
        """Actualiza una evidencia de pago existente"""
        for field in ['file_name', 'file_data']:
            if field in evidence_data:
                setattr(evidence, field, evidence_data[field])
        
        # Note: uploaded_at handled automatically by SQLAlchemy
        return evidence
    
    def delete_payment_evidence(self, site_id: uuid.UUID) -> int:
        """Elimina todas las evidencias de pago de un sitio"""
        evidences = self.get_payment_evidence_by_site(site_id)
        count = len(evidences)
        
        for evidence in evidences:
            self.db.delete(evidence)
        
        return count
    
    def commit(self):
        """Confirma los cambios en la base de datos"""
        self.db.commit()
    
    def rollback(self):
        """Revierte los cambios en la base de datos"""
        self.db.rollback()
    
    def refresh(self, instance):
        """Refresca una instancia desde la base de datos"""
        self.db.refresh(instance)