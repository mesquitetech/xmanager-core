"""
Repository layer for inventory operations
Handles all database interactions for inventory-related data
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid
from datetime import datetime

def get_architecture_connection_by_site_id(db: Session, site_id: uuid.UUID) -> Optional[Dict[str, Any]]:
    """Get architecture connection data for a specific site"""
    try:
        result = db.execute(text("""
            SELECT * FROM site_architecture_connection WHERE site_id = :site_id
        """), {"site_id": site_id}).fetchone()
        
        if not result:
            return None
            
        return dict(result._mapping)
    except Exception as e:
        print(f"Error getting architecture connection: {e}")
        return None

def create_or_update_architecture_connection(db: Session, data: Dict[str, Any]) -> bool:
    """Create or update architecture connection data"""
    try:
        # Check if exists
        existing = db.execute(text("""
            SELECT id FROM site_architecture_connection WHERE site_id = :site_id
        """), {"site_id": data["site_id"]}).fetchone()
        
        if existing:
            # Update
            db.execute(text("""
                UPDATE site_architecture_connection 
                SET tipo = :tipo, tipo_infraestructura = :tipo_infraestructura,
                    carrier_peering = :carrier_peering, tipo_acceso = :tipo_acceso,
                    capacidad = :capacidad, ip_direccionamiento = :ip_direccionamiento,
                    gw = :gw, bgp = :bgp, prefijos_anunciados = :prefijos_anunciados,
                    updated_at = NOW()
                WHERE site_id = :site_id
            """), data)
        else:
            # Insert
            db.execute(text("""
                INSERT INTO site_architecture_connection 
                (site_id, tipo, tipo_infraestructura, carrier_peering, tipo_acceso,
                 capacidad, ip_direccionamiento, gw, bgp, prefijos_anunciados)
                VALUES (:site_id, :tipo, :tipo_infraestructura, :carrier_peering, :tipo_acceso,
                        :capacidad, :ip_direccionamiento, :gw, :bgp, :prefijos_anunciados)
            """), data)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error saving architecture connection: {e}")
        return False

def get_infrastructure_by_site_id(db: Session, site_id: uuid.UUID) -> Optional[Dict[str, Any]]:
    """Get infrastructure data for a specific site"""
    try:
        result = db.execute(text("""
            SELECT * FROM site_infrastructure WHERE site_id = :site_id
        """), {"site_id": site_id}).fetchone()
        
        if not result:
            return None
            
        return dict(result._mapping)
    except Exception as e:
        print(f"Error getting infrastructure: {e}")
        return None

def create_or_update_infrastructure(db: Session, data: Dict[str, Any]) -> bool:
    """Create or update infrastructure data"""
    try:
        # Check if exists
        existing = db.execute(text("""
            SELECT id FROM site_infrastructure WHERE site_id = :site_id
        """), {"site_id": data["site_id"]}).fetchone()
        
        if existing:
            # Update
            db.execute(text("""
                UPDATE site_infrastructure 
                SET tipo_gabinete = :tipo_gabinete, modelo_marca = :modelo_marca,
                    enfriamiento = :enfriamiento, tipo_enfriamiento = :tipo_enfriamiento,
                    potencia_enfriamiento = :potencia_enfriamiento, otras_caracteristicas = :otras_caracteristicas,
                    updated_at = NOW()
                WHERE site_id = :site_id
            """), data)
        else:
            # Insert
            db.execute(text("""
                INSERT INTO site_infrastructure 
                (site_id, tipo_gabinete, modelo_marca, enfriamiento, tipo_enfriamiento,
                 potencia_enfriamiento, otras_caracteristicas)
                VALUES (:site_id, :tipo_gabinete, :modelo_marca, :enfriamiento, :tipo_enfriamiento,
                        :potencia_enfriamiento, :otras_caracteristicas)
            """), data)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error saving infrastructure: {e}")
        return False

def get_logical_connection_by_site_id(db: Session, site_id: uuid.UUID) -> Optional[Dict[str, Any]]:
    """Get logical connection data for a specific site"""
    try:
        result = db.execute(text("""
            SELECT * FROM site_logical_connection WHERE site_id = :site_id
        """), {"site_id": site_id}).fetchone()
        
        if not result:
            return None
            
        return dict(result._mapping)
    except Exception as e:
        print(f"Error getting logical connection: {e}")
        return None

def create_or_update_logical_connection(db: Session, data: Dict[str, Any]) -> bool:
    """Create or update logical connection data"""
    try:
        # Check if exists
        existing = db.execute(text("""
            SELECT id FROM site_logical_connection WHERE site_id = :site_id
        """), {"site_id": data["site_id"]}).fetchone()
        
        if existing:
            # Update
            db.execute(text("""
                UPDATE site_logical_connection 
                SET direccionamiento_clientes = :direccionamiento_clientes,
                    direccionamiento_publico = :direccionamiento_publico,
                    updated_at = NOW()
                WHERE site_id = :site_id
            """), data)
        else:
            # Insert
            db.execute(text("""
                INSERT INTO site_logical_connection 
                (site_id, direccionamiento_clientes, direccionamiento_publico)
                VALUES (:site_id, :direccionamiento_clientes, :direccionamiento_publico)
            """), data)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error saving logical connection: {e}")
        return False

def get_equipment_management_by_site_id(db: Session, site_id: uuid.UUID) -> Optional[Dict[str, Any]]:
    """Get equipment management data for a specific site"""
    try:
        result = db.execute(text("""
            SELECT * FROM site_equipment_management WHERE site_id = :site_id
        """), {"site_id": site_id}).fetchone()
        
        if not result:
            return None
            
        return dict(result._mapping)
    except Exception as e:
        print(f"Error getting equipment management: {e}")
        return None

def create_or_update_equipment_management(db: Session, data: Dict[str, Any]) -> bool:
    """Create or update equipment management data"""
    try:
        # Check if exists
        existing = db.execute(text("""
            SELECT id FROM site_equipment_management WHERE site_id = :site_id
        """), {"site_id": data["site_id"]}).fetchone()
        
        if existing:
            # Update
            db.execute(text("""
                UPDATE site_equipment_management 
                SET core_info = :core_info, switch_info = :switch_info,
                    sensor_luz = :sensor_luz, watchdog_info = :watchdog_info,
                    updated_at = NOW()
                WHERE site_id = :site_id
            """), data)
        else:
            # Insert
            db.execute(text("""
                INSERT INTO site_equipment_management 
                (site_id, core_info, switch_info, sensor_luz, watchdog_info)
                VALUES (:site_id, :core_info, :switch_info, :sensor_luz, :watchdog_info)
            """), data)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error saving equipment management: {e}")
        return False

def get_site_by_id(db: Session, site_id: uuid.UUID) -> Optional[Dict[str, Any]]:
    """Get site information by ID"""
    try:
        from models import Site
        site = db.query(Site).filter(Site.id == site_id).first()
        if not site:
            return None
        return {
            "id": site.id,
            "name": site.name,
            "code": site.code,
            "address": site.address,
            "city": site.city,
            "state": site.state
        }
    except Exception as e:
        print(f"Error getting site: {e}")
        return None