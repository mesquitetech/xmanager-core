from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from auth.utils import get_current_user
from db.database import get_db
from models import User, Site

router = APIRouter(prefix="/api/sites_direct", tags=["sites_direct"])

@router.get("/list_for_expenses", response_model=List[dict])
async def list_sites_for_expenses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtener una lista de sitios simplificada para selector de gastos."""
    sites = db.query(Site).all()
    return [
        {
            "id": str(site.id),
            "name": site.name,
            "code": site.code
        }
        for site in sites
    ]
