"""
API endpoint para verificar si un código de sitio ya existe
"""
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...db.models import Site
from ...auth.utils import get_current_active_user, User

router = APIRouter()

@router.get("/check-code/{code}", response_model=Dict[str, bool])
async def check_site_code_exists(
    code: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Verifica si un código de sitio ya existe en la base de datos.
    """
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se requiere un código para verificar"
        )
    
    # Verificar si ya existe un sitio con ese código
    site = db.query(Site).filter(Site.code == code).first()
    
    return {"exists": site is not None}