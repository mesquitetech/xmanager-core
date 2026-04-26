from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime, timedelta
import json

from repositories.site_repository import SiteRepository
from models import User
from utils.site_utils import generate_site_code


class SiteService:
    """Service principal para todas las operaciones de sitios"""
    
    def __init__(self, site_repository: SiteRepository):
        self.site_repository = site_repository
    
    def get_all_sites(self, current_user: User, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Obtiene todos los sitios con paginación"""
        try:
            skip = (page - 1) * per_page
            sites = self.site_repository.get_all_sites(skip=skip, limit=per_page)
            total_count = self.site_repository.get_site_count()
            
            sites_data = []
            for site in sites:
                site_dict = {
                    "id": str(site.id),
                    "name": site.name,
                    "code": site.code,
                    "address": site.address,
                    "location": site.address,
                    "type": site.site_type,
                    "status": site.status,
                    "latitude": site.latitude,
                    "longitude": site.longitude,
                    "region": site.state,
                    "country": site.country,
                    "city": site.city,
                    "description": site.description,
                    "created_at": site.created_at,
                    "updated_at": site.updated_at,
                    "rb_type": site.rb_type,
                    "height": site.height,
                    "area_type": site.area_type
                }
                
                # Incluir información legal si existe
                if hasattr(site, 'legal_info') and site.legal_info:
                    site_dict["legal_info"] = self._format_legal_info(site.legal_info)
                
                sites_data.append(site_dict)
            
            return {
                "sites": sites_data,
                "pagination": {
                    "current_page": page,
                    "per_page": per_page,
                    "total": total_count,
                    "total_pages": (total_count + per_page - 1) // per_page
                },
                "success": True
            }
        except Exception as e:
            return {
                "error": str(e),
                "sites": [],
                "success": False
            }
    
    def create_site(self, site_data: Dict[str, Any], current_user: User) -> Dict[str, Any]:
        """Crea un nuevo sitio con validaciones"""
        try:
            # Validaciones básicas
            if not site_data.get("name"):
                raise ValueError("El nombre del sitio es obligatorio")
            
            # Procesar y validar datos
            processed_data = self._process_site_data(site_data)
            print("##################################")
            print(processed_data)
            # Crear sitio en base de datos
            new_site = self.site_repository.create_site(processed_data)
            
            # Procesar información legal si existe
            if site_data.get("legal_info"):
                legal_data = site_data["legal_info"]
                # Convert UUID to proper type for repository
                self.site_repository.create_legal_info(new_site.id, legal_data)
            
            # Confirmar transacción
            self.site_repository.commit()
            self.site_repository.refresh(new_site)
            
            # Formatear respuesta
            return self._format_site_response(new_site)
            
        except Exception as e:
            self.site_repository.rollback()
            raise e
    
    def update_site(self, site_id: uuid.UUID, site_data: Dict[str, Any], current_user: User) -> Dict[str, Any]:
        """Actualiza un sitio existente"""
        try:
            # Procesar datos de actualización
            processed_data = self._process_site_update_data(site_data)
            
            # Actualizar sitio (raises ValueError if not found)
            updated_site = self.site_repository.update_site(site_id, processed_data)
            
            # Recargar sitio con relaciones
            site = self.site_repository.get_site_by_id(site_id)
            
            # Procesar información legal si existe
            if site_data.get("legal_info"):
                legal_data = site_data["legal_info"]
                
                if not site.legal_info:
                    # Crear nueva información legal
                    # Convert UUID to proper type for repository
                    self.site_repository.create_legal_info(site.id, legal_data)
                else:
                    # Actualizar información legal existente
                    self.site_repository.update_legal_info(site.legal_info, legal_data)
            
            # Confirmar transacción
            self.site_repository.commit()
            self.site_repository.refresh(updated_site)
            
            return self._format_site_response(updated_site)
            
        except Exception as e:
            self.site_repository.rollback()
            raise e
    
    def get_site_detail(self, site_id: uuid.UUID, current_user: User) -> Dict[str, Any]:
        """Obtiene los detalles completos de un sitio"""
        try:
            site = self.site_repository.get_site_by_id(site_id)
            if not site:
                raise ValueError("Sitio no encontrado")
            
            return self._format_site_response(site)
            
        except Exception as e:
            raise e
    
    def delete_site(self, site_id: uuid.UUID, current_user: User) -> Dict[str, Any]:
        """Elimina un sitio"""
        try:
            # Verificar que el sitio existe
            site = self.site_repository.get_site_by_id(site_id)
            if not site:
                raise ValueError("Sitio no encontrado")
            
            # Eliminar sitio
            success = self.site_repository.delete_site(site_id)
            if success:
                self.site_repository.commit()
                return {
                    "message": "Sitio eliminado correctamente",
                    "site_id": str(site_id),
                    "success": True
                }
            else:
                raise ValueError("No se pudo eliminar el sitio")
                
        except Exception as e:
            self.site_repository.rollback()
            raise e
    
    def search_sites(self, search_term: str, filters: Dict[str, Any], current_user: User) -> Dict[str, Any]:
        """Busca sitios por términos y filtros"""
        try:
            # Validar término de búsqueda
            if search_term and len(search_term.strip()) < 2:
                raise ValueError("El término de búsqueda debe tener al menos 2 caracteres")
            
            sites = self.site_repository.search_sites(search_term, filters)
            
            sites_data = []
            for site in sites:
                sites_data.append(self._format_site_basic(site))
            
            return {
                "sites": sites_data,
                "total": len(sites_data),
                "search_term": search_term,
                "filters": filters,
                "success": True
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "sites": [],
                "success": False
            }
    
    def get_sites_statistics(self, current_user: User) -> Dict[str, Any]:
        """Obtiene estadísticas de sitios"""
        try:
            stats = self.site_repository.get_sites_statistics()
            return {
                "statistics": stats,
                "success": True
            }
        except Exception as e:
            return {
                "error": str(e),
                "statistics": {},
                "success": False
            }
    
    def process_payment(self, site_id: uuid.UUID, payment_data: Dict[str, Any], current_user: User) -> Dict[str, Any]:
        """Procesa un pago y actualiza la fecha de próximo pago"""
        try:
            # Verificar que el sitio existe
            site = self.site_repository.get_site_by_id(site_id)
            if not site:
                raise ValueError("Sitio no encontrado")
            
            # Crear evidencia de pago si se proporciona
            if payment_data.get("evidence"):
                evidence_data = payment_data["evidence"]
                # Convert UUID to proper type for repository
                self.site_repository.create_payment_evidence(
                    site_id, evidence_data, current_user.id
                )
            
            # Actualizar fecha de próximo pago basado en frecuencia
            if site.legal_info and payment_data.get("payment_date"):
                next_payment = self._calculate_next_payment_date(
                    payment_data["payment_date"],
                    site.legal_info.payment_frequency
                )
                
                self.site_repository.update_legal_info(
                    site.legal_info,
                    {"next_payment_date": next_payment}
                )
            
            self.site_repository.commit()
            
            return {
                "message": "Pago procesado correctamente",
                "site_id": str(site_id),
                "success": True
            }
            
        except Exception as e:
            self.site_repository.rollback()
            raise e
    
    def _process_site_data(self, site_data: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa y valida datos de sitio para creación"""
        processed = {
            'name': site_data['name'],
            'code': site_data.get('code', generate_site_code()),
            'site_type': site_data.get('type', 'TOWER'),
            'status': site_data.get('status', 'ACTIVE'),
            'description': site_data.get('description', '')
        }
        
        # Procesar ubicación y dirección
        if 'address' in site_data:
            processed['address'] = site_data['address']
        elif 'location' in site_data:
            processed['address'] = site_data['location']
        
        # Procesar región/estado
        if 'region' in site_data:
            processed['state'] = site_data['region']
        
        # Procesar coordenadas
        latitude, longitude = self._parse_coordinates(site_data)
        processed['latitude'] = latitude
        processed['longitude'] = longitude
        
        # Procesar campos adicionales
        processed['rb_type'] = site_data.get('rb_type', '')
        processed['area_type'] = site_data.get('area_type', '')
        
        if site_data.get('height'):
            try:
                processed['height'] = float(site_data['height'])
            except (ValueError, TypeError):
                processed['height'] = None
        
        return processed
    
    def _process_site_update_data(self, site_data: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa datos para actualización de sitio"""
        processed = {}
        
        # Solo incluir campos que están presentes
        field_mapping = {
            'name': 'name',
            'code': 'code',
            'type': 'site_type',
            'status': 'status',
            'description': 'description',
            'address': 'address',
            'location': 'address',
            'region': 'state',
            'rb_type': 'rb_type',
            'area_type': 'area_type'
        }
        
        for source_field, target_field in field_mapping.items():
            if source_field in site_data:
                processed[target_field] = site_data[source_field]
        
        # Procesar coordenadas si están presentes
        if 'latitude' in site_data or 'longitude' in site_data or 'coordinates' in site_data:
            latitude, longitude = self._parse_coordinates(site_data)
            processed['latitude'] = latitude
            processed['longitude'] = longitude
        
        # Procesar altura
        if 'height' in site_data:
            try:
                processed['height'] = float(site_data['height']) if site_data['height'] else None
            except (ValueError, TypeError):
                processed['height'] = None
        
        return processed
    
    def _parse_coordinates(self, site_data: Dict[str, Any]) -> tuple:
        """Parsea coordenadas desde diferentes formatos"""
        latitude = site_data.get('latitude')
        longitude = site_data.get('longitude')
        
        # Si no hay lat/lng directamente, intentar usar coordinates
        if (latitude is None or longitude is None) and 'coordinates' in site_data:
            try:
                coords = site_data['coordinates']
                if isinstance(coords, str) and ',' in coords:
                    lat_str, lng_str = coords.split(',')
                    latitude = float(lat_str.strip())
                    longitude = float(lng_str.strip())
            except (ValueError, TypeError):
                pass
        
        # Convertir a float
        try:
            latitude = float(latitude) if latitude is not None else 0.0
            longitude = float(longitude) if longitude is not None else 0.0
        except (ValueError, TypeError):
            latitude, longitude = 0.0, 0.0
        
        return latitude, longitude
    
    def _calculate_next_payment_date(self, payment_date: str, frequency: str) -> datetime:
        """Calcula la fecha del próximo pago basado en la frecuencia"""
        try:
            if isinstance(payment_date, str):
                current_date = datetime.fromisoformat(payment_date.replace('Z', '+00:00'))
            else:
                current_date = payment_date
            
            frequency_map = {
                'monthly': 30,
                'quarterly': 90,
                'semiannual': 180,
                'annual': 365,
                'biannual': 730
            }
            
            days_to_add = frequency_map.get(frequency.lower(), 30)
            return current_date + timedelta(days=days_to_add)
            
        except Exception:
            return datetime.now() + timedelta(days=30)
    
    def _format_site_response(self, site) -> Dict[str, Any]:
        """Formatea la respuesta de un sitio con toda la información"""
        response = {
            "id": str(site.id),
            "name": site.name,
            "code": site.code,
            "address": site.address,
            "location": site.address,
            "type": site.site_type,
            "status": site.status,
            "latitude": site.latitude,
            "longitude": site.longitude,
            "region": site.state,
            "country": site.country,
            "city": site.city,
            "description": site.description,
            "created_at": site.created_at,
            "updated_at": site.updated_at,
            "rb_type": site.rb_type,
            "height": site.height,
            "area_type": site.area_type
        }
        
        # Incluir información legal si existe
        if hasattr(site, 'legal_info') and site.legal_info:
            response["legal_info"] = self._format_legal_info(site.legal_info)
        
        return response
    
    def _format_site_basic(self, site) -> Dict[str, Any]:
        """Formatea información básica de un sitio"""
        return {
            "id": str(site.id),
            "name": site.name,
            "code": site.code,
            "address": site.address,
            "type": site.site_type,
            "status": site.status,
            "region": site.state
        }
    
    def _format_legal_info(self, legal_info) -> Dict[str, Any]:
        """Formatea información legal de un sitio"""
        return {
            "landlord_name": legal_info.landlord_name,
            "landlord_contact": legal_info.landlord_contact,
            "landlord_email": legal_info.landlord_email,
            "contract_start_date": legal_info.contract_start_date,
            "contract_end_date": legal_info.contract_end_date,
            "monthly_rent": legal_info.monthly_rent,
            "currency": legal_info.currency,
            "payment_frequency": legal_info.payment_frequency,
            "next_payment_date": legal_info.next_payment_date,
            "service_provider": legal_info.service_provider,
            "electricity_support": legal_info.electricity_support,
            "internet_exchange": legal_info.internet_exchange,
            "notes": legal_info.notes
        }