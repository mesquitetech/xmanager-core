from sqlalchemy.orm import Session
from fastapi import HTTPException
from repositories.carrier_repository import get_carrier_by_id, delete_carrier
from repositories.carrier_repository import create_carrier_in_db
from api.carriers.schemas import CarrierCreate
from typing import List, Dict, Any, Optional
from repositories.carrier_repository import get_filtered_carriers

def get_carriers_logic(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
) -> List[Dict[str, Any]]:
    try:
        carriers = get_filtered_carriers(db, skip, limit, search)

        result = []
        for carrier in carriers:
            result.append({
                "id": carrier.id,
                "plaza": carrier.plaza or "",
                "zona": carrier.zona or "",
                "proveedor": carrier.proveedor or "",
                "ancho_banda": carrier.ancho_banda or "",
                "ip": carrier.ip or "",
                "contacto": carrier.contacto or "",
                "email": carrier.email or "",
                "telefono": carrier.telefono or "",
                "notas": carrier.notas or "",
                "created_at": carrier.created_at.isoformat() if carrier.created_at else None,
                "updated_at": carrier.updated_at.isoformat() if carrier.updated_at else None
            })

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener carriers: {str(e)}")

def create_carrier_logic(db: Session, carrier_data: CarrierCreate, user_email: str) -> dict:
    try:
        carrier_dict = carrier_data.model_dump()
        carrier_dict['created_by'] = user_email

        new_carrier = create_carrier_in_db(db, carrier_dict)
        return {
            "id": new_carrier.id,
            "message": "Carrier creado exitosamente"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear carrier: {str(e)}")


def delete_carrier_logic(db: Session, carrier_id: int):
    carrier = get_carrier_by_id(db, carrier_id)
    if not carrier:
        raise HTTPException(status_code=404, detail="Carrier no encontrado")

    try:
        delete_carrier(db, carrier)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar carrier: {str(e)}")