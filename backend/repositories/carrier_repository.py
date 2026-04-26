"""
Repository layer for Carrier operations
Handles all database interactions for carriers (telecommunications providers)
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import uuid

from models import Carrier


def get_filtered_carriers(db: Session, skip: int = 0, limit: int = 100, search: Optional[str] = None):
    """Get filtered carriers from database with optional search"""
    try:
        query = db.query(Carrier)
        
        # Apply search filter if provided
        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    Carrier.plaza.ilike(search_term),
                    Carrier.proveedor.ilike(search_term),
                    Carrier.ip.ilike(search_term),
                    Carrier.contacto.ilike(search_term),
                    Carrier.email.ilike(search_term)
                )
            )
        
        carriers = query.offset(skip).limit(limit).all()
        return carriers
        
    except Exception as e:
        print(f"Error getting carriers: {e}")
        return []


def create_carrier_in_db(db: Session, carrier_data: Dict[str, Any]):
    """Create new carrier in database"""
    try:
        new_carrier = Carrier(**carrier_data)
        db.add(new_carrier)
        db.commit()
        db.refresh(new_carrier)
        return new_carrier
        
    except Exception as e:
        db.rollback()
        print(f"Error creating carrier: {e}")
        return None


def get_carrier_by_id(db: Session, carrier_id: int):
    """Get carrier by ID"""
    try:
        return db.query(Carrier).filter(Carrier.id == carrier_id).first()
    except Exception as e:
        print(f"Error getting carrier: {e}")
        return None


def update_carrier_in_db(db: Session, carrier_id: int, carrier_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update carrier in database"""
    try:
        carrier = db.query(Carrier).filter(Carrier.id == carrier_id).first()
        if not carrier:
            return None
            
        # Update fields
        for field, value in carrier_data.items():
            if hasattr(carrier, field) and value is not None:
                setattr(carrier, field, value)
        
        db.commit()
        db.refresh(carrier)
        
        return {
            "id": carrier.id,
            "plaza": carrier.plaza,
            "zona": carrier.zona,
            "proveedor": carrier.proveedor,
            "ancho_banda": carrier.ancho_banda,
            "ip": carrier.ip,
            "contacto": carrier.contacto,
            "email": carrier.email,
            "telefono": carrier.telefono,
            "notas": carrier.notas,
            "created_at": carrier.created_at,
            "updated_at": carrier.updated_at
        }
        
    except Exception as e:
        db.rollback()
        print(f"Error updating carrier: {e}")
        return None


def delete_carrier(db: Session, carrier):
    """Delete carrier from database"""
    try:
        db.delete(carrier)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error deleting carrier: {e}")
        raise


def check_carrier_ip_exists(db: Session, ip: str, exclude_id: Optional[int] = None) -> bool:
    """Check if IP address already exists (for validation)"""
    try:
        query = db.query(Carrier).filter(Carrier.ip == ip)
        if exclude_id:
            query = query.filter(Carrier.id != exclude_id)
        
        return query.first() is not None
        
    except Exception as e:
        print(f"Error checking carrier IP: {e}")
        return False


def get_carriers_count(db: Session, search: Optional[str] = None) -> int:
    """Get total count of carriers (for pagination)"""
    try:
        query = db.query(Carrier)
        
        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    Carrier.plaza.ilike(search_term),
                    Carrier.proveedor.ilike(search_term),
                    Carrier.ip.ilike(search_term),
                    Carrier.contacto.ilike(search_term),
                    Carrier.email.ilike(search_term)
                )
            )
        
        return query.count()
        
    except Exception as e:
        print(f"Error counting carriers: {e}")
        return 0


def get_carriers_by_plaza(db: Session, plaza: str) -> List[Dict[str, Any]]:
    """Get carriers filtered by plaza"""
    try:
        carriers = db.query(Carrier).filter(Carrier.plaza.ilike(f"%{plaza}%")).all()
        
        result = []
        for carrier in carriers:
            carrier_data = {
                "id": carrier.id,
                "plaza": carrier.plaza,
                "zona": carrier.zona,
                "proveedor": carrier.proveedor,
                "ancho_banda": carrier.ancho_banda,
                "ip": carrier.ip,
                "contacto": carrier.contacto,
                "email": carrier.email,
                "telefono": carrier.telefono,
                "notas": carrier.notas,
                "created_at": carrier.created_at,
                "updated_at": carrier.updated_at
            }
            result.append(carrier_data)
        
        return result
        
    except Exception as e:
        print(f"Error getting carriers by plaza: {e}")
        return []


def get_carriers_by_provider(db: Session, proveedor: str) -> List[Dict[str, Any]]:
    """Get carriers filtered by provider"""
    try:
        carriers = db.query(Carrier).filter(Carrier.proveedor.ilike(f"%{proveedor}%")).all()
        
        result = []
        for carrier in carriers:
            carrier_data = {
                "id": carrier.id,
                "plaza": carrier.plaza,
                "zona": carrier.zona,
                "proveedor": carrier.proveedor,
                "ancho_banda": carrier.ancho_banda,
                "ip": carrier.ip,
                "contacto": carrier.contacto,
                "email": carrier.email,
                "telefono": carrier.telefono,
                "notas": carrier.notas,
                "created_at": carrier.created_at,
                "updated_at": carrier.updated_at
            }
            result.append(carrier_data)
        
        return result
        
    except Exception as e:
        print(f"Error getting carriers by provider: {e}")
        return []