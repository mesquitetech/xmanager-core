from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid

from pydantic_core import ValidationError

from repositories.site_repository_complete import SiteRepository
from utils.site_utils import generate_site_code
from models import User

class SiteNotFoundError(Exception):
    pass


class SiteServiceComplete:
    """Service para lógica de negocio de sitios completos"""
    
    def __init__(self, site_repository: SiteRepository):
        self.site_repository = site_repository
    
    def create_site(self, site_data: Dict[str, Any], current_user: User) -> Dict[str, Any]:
        """Crea un nuevo sitio con validaciones y lógica de negocio"""
        # Validar campos requeridos
        if not site_data.get("name"):
            raise ValueError("El nombre del sitio es obligatorio")
        
        # Generar código de sitio si no se proporciona
        code = site_data.get("code", generate_site_code())
        
        # Procesar y validar datos de entrada
        processed_data = self._process_site_data(site_data, code)
        
        try:
            # Crear sitio en base de datos
            new_site = self.site_repository.create_site(processed_data)
            
            # Procesar información legal si existe
            if site_data.get("legal_info"):
                legal_data = site_data["legal_info"]
                self.site_repository.create_legal_info(new_site.id, legal_data)
            
            # Confirmar transacción
            self.site_repository.commit()
            self.site_repository.refresh(new_site)
            
            # Preparar respuesta
            return self._format_site_response(new_site)
            
        except Exception as e:
            self.site_repository.rollback()
            raise Exception(f"Error al crear el sitio en la base de datos: {str(e)}")

    def update_site(self, site_id: uuid.UUID, site_data: Dict[str, Any], current_user: User) -> Dict[str, Any]:
        """Actualiza un sitio existente con validaciones"""
        # Buscar sitio
        site = self.site_repository.get_site_by_id(site_id)
        if not site:
            raise ValueError("Sitio no encontrado")
        
        try:
            # Procesar datos de actualización
            update_data = self._process_update_data(site_data)
            
            # Actualizar sitio
            updated_site = self.site_repository.update_site(site, update_data)
            
            # Procesar información legal si existe
            if site_data.get("legal_info"):
                legal_data = site_data["legal_info"]
                
                if not site.legal_info:
                    # Crear nueva información legal
                    self.site_repository.create_legal_info(site.id, legal_data)
                else:
                    # Actualizar información legal existente
                    self.site_repository.update_legal_info(site.legal_info, legal_data)
            
            # Confirmar transacción
            self.site_repository.commit()
            self.site_repository.refresh(updated_site)
            
            # Preparar respuesta
            return self._format_site_response(updated_site)
            
        except Exception as e:
            self.site_repository.rollback()
            raise Exception(f"Error al actualizar el sitio en la base de datos: {str(e)}")
    ####################CODIGO EN CORECCION###########################
    def get_all_sites(self, current_user: User) -> List[Dict[str, Any]]:
        """Obtiene todos los sitios con formato de respuesta"""
        try:
            sites = self.site_repository.get_all_sites()
            return [self._format_site_response(site) for site in sites]
            
        except Exception as e:
            raise Exception(f"Error al obtener la lista de sitios: {str(e)}")
    
    def get_site_detail(self, site_id: uuid.UUID, current_user: User) -> Dict[str, Any]:
        """Obtiene detalles de un sitio específico"""
        site = self.site_repository.get_site_by_id(site_id)
        if not site:
            raise ValueError("Sitio no encontrado")
        
        return self._format_site_response(site)

    def get_site_deleted(self, site_id: uuid.UUID, current_user: User) -> bool:
        """Elimina un sitio específico"""

        deleted = self.site_repository.delete_site(site_id)
        print(f"SITE DELETED --> {deleted} linea 110")
        if not deleted:
            raise ValidationError("Sitio no encontrado")

        return True
        
    
    def process_payment(self, site_id: uuid.UUID, payment_data: Dict[str, Any], current_user: User) -> Dict[str, Any]:
        """Procesa pagos y maneja evidencias con lógica de negocio"""
        # Buscar sitio
        site = self.site_repository.get_site_by_id(site_id)
        if not site:
            raise ValueError("Sitio no encontrado")
        
        if not site.legal_info:
            raise ValueError("El sitio no tiene información de arrendamiento configurada")
        
        try:
            # Determinar tipo de operación
            is_update = payment_data.get("is_update", False)
            delete_evidence = payment_data.get("delete_evidence", False)
            
            if delete_evidence:
                result = self._process_delete_evidence(site, payment_data, current_user)
            elif is_update:
                result = self._process_update_evidence(site, payment_data, current_user)
            else:
                result = self._process_new_payment(site, payment_data, current_user)
            
            # Confirmar transacción
            self.site_repository.commit()
            self.site_repository.refresh(site)
            
            return result
            
        except Exception as e:
            self.site_repository.rollback()
            raise Exception(f"Error al procesar el pago: {str(e)}")
    
    def _process_site_data(self, site_data: Dict[str, Any], code: str) -> Dict[str, Any]:
        """Procesa y valida datos de entrada para crear sitio"""
        processed = {
            'name': site_data.get('name'),
            'code': code,
            'site_type': site_data.get('type', 'TOWER'),
            'status': site_data.get('status', 'ACTIVE'),
            'description': site_data.get('description', ''),
            'rb_type': site_data.get('rb_type', ''),
            'area_type': site_data.get('area_type', '')
        }
        
        # Procesar altura
        height = site_data.get('height')
        try:
            processed['height'] = float(height) if height is not None else None
        except (ValueError, TypeError):
            processed['height'] = None
        
        # Procesar ubicación
        address = site_data.get('address', '')
        region = site_data.get('region', '')
        
        location = address
        if region and not location.lower().endswith(region.lower()):
            location = f"{location}, {region}" if location else region
        
        # Procesar campos de dirección
        address_parts = location.split(",")
        processed.update({
            'address': location,
            'city': address_parts[0].strip() if len(address_parts) > 0 else "",
            'state': region or (address_parts[1].strip() if len(address_parts) > 1 else ""),
            'country': address_parts[2].strip() if len(address_parts) > 2 else "México"
        })
        
        # Procesar coordenadas
        latitude, longitude = self._process_coordinates(site_data)
        processed.update({
            'latitude': latitude,
            'longitude': longitude
        })
        
        return processed
    
    def _process_update_data(self, site_data: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa datos para actualización de sitio"""
        update_data = {}
        
        # Campos básicos
        for field in ['name', 'code', 'description', 'rb_type', 'area_type']:
            if field in site_data:
                update_data[field] = site_data[field]
        
        # Mapear campos con nombres diferentes
        if 'type' in site_data:
            update_data['site_type'] = site_data['type']
        
        if 'status' in site_data:
            update_data['status'] = site_data['status']
        
        # Procesar altura
        if 'height' in site_data:
            try:
                update_data['height'] = float(site_data['height']) if site_data['height'] is not None else None
            except (ValueError, TypeError):
                update_data['height'] = None
        
        # Procesar ubicación
        if 'address' in site_data or 'region' in site_data:
            address = site_data.get('address', '')
            region = site_data.get('region', '')
            
            if address:
                update_data['address'] = address
                parts = address.split(",")
                if parts:
                    update_data['city'] = parts[0].strip()
            
            if region:
                update_data['state'] = region
        
        # Procesar coordenadas
        if 'latitude' in site_data or 'longitude' in site_data or 'coordinates' in site_data:
            latitude, longitude = self._process_coordinates(site_data)
            update_data.update({
                'latitude': latitude,
                'longitude': longitude
            })
        
        return update_data
    
    def _process_coordinates(self, site_data: Dict[str, Any]) -> tuple:
        """Procesa y valida coordenadas"""
        latitude = site_data.get("latitude")
        longitude = site_data.get("longitude")
        
        # Si no se proporcionaron lat/lng directamente, intentar usar coordinates
        if not latitude and not longitude and "coordinates" in site_data:
            try:
                coords = site_data["coordinates"]
                if isinstance(coords, str) and "," in coords:
                    lat_str, lng_str = coords.split(",")
                    latitude = float(lat_str.strip())
                    longitude = float(lng_str.strip())
            except (ValueError, TypeError):
                pass
        
        # Convertir a float
        try:
            latitude = float(latitude) if latitude else 0.0
            longitude = float(longitude) if longitude else 0.0
        except (ValueError, TypeError):
            latitude, longitude = 0.0, 0.0
        
        return latitude, longitude
    
    def _process_delete_evidence(self, site, payment_data: Dict[str, Any], current_user: User) -> Dict[str, Any]:
        """Procesa eliminación de evidencia de pago"""
        # Calcular fecha anterior según frecuencia
        frequency = site.legal_info.payment_frequency
        current_date = site.legal_info.next_payment_date
        next_payment_date = payment_data.get("next_payment_date")
        
        if not next_payment_date and current_date:
            next_payment_date = self._calculate_previous_date(current_date, frequency)
        
        # Actualizar información legal
        legal_update = {
            'payment_status': 'unpaid',
            'payment_evidence_file': None,
            'payment_evidence_type': None
        }
        
        if next_payment_date:
            legal_update['next_payment_date'] = next_payment_date
        
        self.site_repository.update_legal_info(site.legal_info, legal_update)
        
        # Eliminar registros de evidencia
        count = self.site_repository.delete_payment_evidence(site.id)
        
        return {
            "site_id": str(site.id),
            "site_name": site.name,
            "operation": "delete_evidence",
            "processed_at": datetime.utcnow().isoformat(),
            "processed_by": current_user.email,
            "evidences_deleted": count,
            "message": "Comprobante eliminado correctamente"
        }
    
    def _process_update_evidence(self, site, payment_data: Dict[str, Any], current_user: User) -> Dict[str, Any]:
        """Procesa actualización de evidencia de pago"""
        file_data = payment_data.get("file_data")
        file_name = payment_data.get("file_name")
        file_type = payment_data.get("file_type")
        
        if not file_data or not file_name:
            raise ValueError("Se requiere un archivo para actualizar el comprobante")
        
        # Actualizar información legal
        legal_update = {
            'payment_evidence_file': file_name,
            'payment_evidence_type': file_type,
            'payment_status': 'paid'
        }
        
        self.site_repository.update_legal_info(site.legal_info, legal_update)
        
        # Actualizar o crear evidencia
        evidences = self.site_repository.get_payment_evidence_by_site(site.id)
        
        if evidences:
            # Actualizar existente
            evidence = evidences[0]
            self.site_repository.update_payment_evidence(evidence, {
                'file_name': file_name,
                'file_data': file_data
            })
        else:
            # Crear nueva
            self.site_repository.create_payment_evidence({
                'site_id': site.id,
                'file_name': file_name,
                'file_data': file_data,
                'uploaded_by_id': current_user.id
            })
        
        return {
            "site_id": str(site.id),
            "site_name": site.name,
            "operation": "update_evidence",
            "processed_at": datetime.utcnow().isoformat(),
            "processed_by": current_user.email,
            "message": "Comprobante actualizado correctamente"
        }
    
    def _process_new_payment(self, site, payment_data: Dict[str, Any], current_user: User) -> Dict[str, Any]:
        """Procesa nuevo pago con evidencia"""
        file_data = payment_data.get("file_data")
        file_name = payment_data.get("file_name")
        file_type = payment_data.get("file_type")
        next_payment_date = payment_data.get("next_payment_date")
        
        # Calcular próxima fecha de pago si no se proporciona
        if not next_payment_date:
            frequency = site.legal_info.payment_frequency
            current_date = site.legal_info.next_payment_date or datetime.now()
            next_payment_date = self._calculate_next_payment_date(current_date, frequency)
        
        # Actualizar información legal
        legal_update = {
            'next_payment_date': next_payment_date,
            'payment_status': 'paid'
        }
        
        if file_name:
            legal_update.update({
                'payment_evidence_file': file_name,
                'payment_evidence_type': file_type
            })
        
        self.site_repository.update_legal_info(site.legal_info, legal_update)
        
        # Crear evidencia si hay archivo
        if file_data and file_name:
            self.site_repository.create_payment_evidence({
                'site_id': site.id,
                'file_name': file_name,
                'file_data': file_data,
                'uploaded_by_id': current_user.id
            })
        
        return {
            "site_id": str(site.id),
            "site_name": site.name,
            "operation": "new_payment",
            "processed_at": datetime.utcnow().isoformat(),
            "processed_by": current_user.email,
            "next_payment_date": next_payment_date,
            "message": "Pago procesado correctamente"
        }
    
    def _calculate_previous_date(self, current_date, frequency: str) -> str:
        """Calcula la fecha anterior según la frecuencia de pago"""
        if isinstance(current_date, str):
            current_date = datetime.fromisoformat(current_date.replace('Z', '+00:00'))
        
        if frequency == "monthly":
            if current_date.month == 1:
                new_date = current_date.replace(year=current_date.year-1, month=12)
            else:
                new_date = current_date.replace(month=current_date.month-1)
        elif frequency == "biweekly":
            new_date = current_date - timedelta(days=14)
        elif frequency == "quarterly":
            if current_date.month <= 3:
                new_date = current_date.replace(year=current_date.year-1, month=current_date.month+9)
            else:
                new_date = current_date.replace(month=current_date.month-3)
        elif frequency == "semiannual":
            if current_date.month <= 6:
                new_date = current_date.replace(year=current_date.year-1, month=current_date.month+6)
            else:
                new_date = current_date.replace(month=current_date.month-6)
        elif frequency == "annual":
            new_date = current_date.replace(year=current_date.year-1)
        else:
            new_date = current_date
        
        return new_date.isoformat()
    
    def _calculate_next_payment_date(self, current_date, frequency: str) -> str:
        """Calcula la próxima fecha de pago según la frecuencia"""
        if isinstance(current_date, str):
            current_date = datetime.fromisoformat(current_date.replace('Z', '+00:00'))
        
        if frequency == "monthly":
            if current_date.month == 12:
                new_date = current_date.replace(year=current_date.year+1, month=1)
            else:
                new_date = current_date.replace(month=current_date.month+1)
        elif frequency == "biweekly":
            new_date = current_date + timedelta(days=14)
        elif frequency == "quarterly":
            if current_date.month >= 10:
                new_date = current_date.replace(year=current_date.year+1, month=current_date.month-9)
            else:
                new_date = current_date.replace(month=current_date.month+3)
        elif frequency == "semiannual":
            if current_date.month >= 7:
                new_date = current_date.replace(year=current_date.year+1, month=current_date.month-6)
            else:
                new_date = current_date.replace(month=current_date.month+6)
        elif frequency == "annual":
            new_date = current_date.replace(year=current_date.year+1)
        else:
            new_date = current_date + timedelta(days=30)  # Default monthly
        
        return new_date.isoformat()
    
    def _format_site_response(self, site) -> Dict[str, Any]:
        """Formatea la respuesta del sitio con toda la información"""
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
        if site.legal_info:
            response["legal_info"] = {
                "landlord_name": site.legal_info.landlord_name,
                "landlord_contact": site.legal_info.landlord_contact,
                "landlord_email": site.legal_info.landlord_email,
                "contract_start_date": site.legal_info.contract_start_date,
                "contract_end_date": site.legal_info.contract_end_date,
                "monthly_rent": site.legal_info.monthly_rent,
                "currency": site.legal_info.currency,
                "payment_frequency": site.legal_info.payment_frequency,
                "next_payment_date": site.legal_info.next_payment_date,
                "payment_status": site.legal_info.payment_status,
                "payment_evidence_file": site.legal_info.payment_evidence_file,
                "payment_evidence_type": site.legal_info.payment_evidence_type,
                "service_provider": site.legal_info.service_provider,
                "electricity_support": site.legal_info.electricity_support,
                "internet_exchange": site.legal_info.internet_exchange,
                "notes": site.legal_info.notes,
                "period": site.legal_info.period,
                "noc_status": site.legal_info.noc_status,
                "infra_status": site.legal_info.infra_status,
                "network_arch_status": site.legal_info.network_arch_status,
                "classification": site.legal_info.classification,
                "contract_date": site.legal_info.contract_date,
                "requires_invoice": site.legal_info.requires_invoice,
                "courtesy_service": site.legal_info.courtesy_service,
                "courtesy_service_details": site.legal_info.courtesy_service_details,
                "landlord_phone": site.legal_info.landlord_phone
            }
        
        return response