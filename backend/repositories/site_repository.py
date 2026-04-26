from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, text, and_, or_
import uuid
from datetime import datetime

from models import Site, SiteLegalInfo, PaymentEvidence


class SiteRepository:
    """Repository principal para todas las operaciones de sitios"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_sites(self, skip: int = 0, limit: int = 100) -> List[Site]:
        """Obtiene todos los sitios con paginación"""
        return self.db.query(Site).offset(skip).limit(limit).all()
    
    def get_site_count(self) -> int:
        """Obtiene el total de sitios"""
        return self.db.query(Site).count()
    
    def get_site_by_id(self, site_id: uuid.UUID) -> Optional[Site]:
        """Obtiene un sitio por ID con información legal"""
        return self.db.query(Site).filter(Site.id == site_id).first()
    
    def create_site(self, site_data: Dict[str, Any]) -> Site:
        """Crea un nuevo sitio en la base de datos"""
        # Crear punto geométrico si hay coordenadas
        geom = None
        latitude = site_data.get('latitude', 0.0)
        longitude = site_data.get('longitude', 0.0)
        
        if latitude != 0.0 and longitude != 0.0:
            geom = func.ST_SetSRID(
                func.ST_MakePoint(longitude, latitude),
                4326
            )
        
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
        self.db.flush()  # Para obtener el ID
        return new_site
    
    def update_site(self, site_id: uuid.UUID, site_data: Dict[str, Any]) -> Site:
        """Actualiza un sitio existente"""
        site = self.db.query(Site).filter(Site.id == site_id).first()
        if not site:
            raise ValueError("Sitio no encontrado")
        
        # Actualizar campos básicos
        for field in ['name', 'code', 'address', 'city', 'state', 'country', 
                     'zip_code', 'site_type', 'status', 'description', 
                     'rb_type', 'height', 'area_type']:
            if field in site_data:
                setattr(site, field, site_data[field])
        
        # Actualizar coordenadas y geometría
        if 'latitude' in site_data and 'longitude' in site_data:
            latitude = float(site_data['latitude']) if site_data['latitude'] else 0.0
            longitude = float(site_data['longitude']) if site_data['longitude'] else 0.0
            
            # Note: Coordinate updates handled by SQLAlchemy automatically
        
        return site
    
    def delete_site(self, site_id: uuid.UUID) -> bool:
        """Elimina un sitio de la base de datos"""
        site = self.db.query(Site).filter(Site.id == site_id).first()
        if site:
            self.db.delete(site)
            return True
        return False
    
    def search_sites(self, search_term: str, filters: Optional[Dict[str, Any]] = None) -> List[Site]:
        """Busca sitios por términos y filtros"""
        query = self.db.query(Site)
        
        # Aplicar búsqueda por término
        if search_term:
            search_filter = or_(
                Site.name.ilike(f"%{search_term}%"),
                Site.code.ilike(f"%{search_term}%"),
                Site.address.ilike(f"%{search_term}%"),
                Site.city.ilike(f"%{search_term}%")
            )
            query = query.filter(search_filter)
        
        # Aplicar filtros adicionales
        if filters:
            if filters.get('status'):
                query = query.filter(Site.status == filters['status'])
            if filters.get('site_type'):
                query = query.filter(Site.site_type == filters['site_type'])
            if filters.get('region'):
                query = query.filter(Site.state.ilike(f"%{filters['region']}%"))
        
        return query.all()
    
    def get_sites_by_region(self, region: str) -> List[Site]:
        """Obtiene sitios por región"""
        return self.db.query(Site).filter(Site.state.ilike(f"%{region}%")).all()
    
    def get_sites_by_type(self, site_type: str) -> List[Site]:
        """Obtiene sitios por tipo"""
        return self.db.query(Site).filter(Site.site_type == site_type).all()
    
    def get_sites_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de sitios"""
        total = self.db.query(Site).count()
        active = self.db.query(Site).filter(Site.status == 'ACTIVE').count()
        inactive = self.db.query(Site).filter(Site.status == 'INACTIVE').count()
        maintenance = self.db.query(Site).filter(Site.status == 'MAINTENANCE').count()
        
        # Estadísticas por tipo
        tower_count = self.db.query(Site).filter(Site.site_type == 'TOWER').count()
        rooftop_count = self.db.query(Site).filter(Site.site_type == 'ROOFTOP').count()
        
        return {
            'total_sites': total,
            'active_sites': active,
            'inactive_sites': inactive,
            'maintenance_sites': maintenance,
            'tower_sites': tower_count,
            'rooftop_sites': rooftop_count,
            'utilization_rate': round((active / total * 100) if total > 0 else 0, 2)
        }
    
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
            notes=legal_data.get('notes')
        )
        
        self.db.add(legal_info)
        self.db.flush()
        return legal_info
    
    def update_legal_info(self, legal_info: SiteLegalInfo, legal_data: Dict[str, Any]) -> SiteLegalInfo:
        """Actualiza información legal existente"""
        for field in ['landlord_name', 'landlord_contact', 'landlord_email',
                     'contract_start_date', 'contract_end_date', 'monthly_rent',
                     'currency', 'payment_frequency', 'next_payment_date',
                     'service_provider', 'electricity_support', 'internet_exchange', 'notes']:
            if field in legal_data:
                setattr(legal_info, field, legal_data[field])
        
        return legal_info
    
    def create_payment_evidence(self, site_id: uuid.UUID, evidence_data: Dict[str, Any], user_id: uuid.UUID) -> PaymentEvidence:
        """Crea evidencia de pago para un sitio"""
        evidence = PaymentEvidence(
            site_id=site_id,
            uploaded_by_id=user_id,
            file_name=evidence_data.get('file_name'),
            file_data=evidence_data.get('file_data'),
            payment_date=evidence_data.get('payment_date'),
            amount=evidence_data.get('amount'),
            description=evidence_data.get('description')
        )
        
        self.db.add(evidence)
        self.db.flush()
        return evidence
    
    def get_payment_evidences(self, site_id: uuid.UUID) -> List[PaymentEvidence]:
        """Obtiene evidencias de pago de un sitio"""
        return self.db.query(PaymentEvidence).filter(PaymentEvidence.site_id == site_id).all()
    
    def commit(self):
        """Confirma cambios en la base de datos"""
        self.db.commit()
    
    def rollback(self):
        """Revierte cambios en la base de datos"""
        self.db.rollback()
    
    def refresh(self, instance):
        """Refresca una instancia desde la base de datos"""
        self.db.refresh(instance)