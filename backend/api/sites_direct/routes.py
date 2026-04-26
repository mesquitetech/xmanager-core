"""
API para operaciones directas con sitios
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...db.models import Site
from ...auth.utils import get_current_active_user, User

router = APIRouter()

@router.get("/check-code/{code}")
async def check_site_code(
    code: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Verifica si un código de sitio ya existe
    """
    site = db.query(Site).filter(Site.code == code).first()
    
    return {"exists": site is not None, "code": code}