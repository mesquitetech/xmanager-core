from typing import List, Optional
from uuid import UUID
import datetime

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from db.database import get_db
from models import OperationalExpense, ExpenseCategory, User, Site, ExpenseEvidence
from auth.utils import get_current_user
from utils.storage import upload_file, create_signed_url, delete_file, BUCKETS

router = APIRouter()
"""
name: name,
category: concept,
amount: parseFloat(amount),
expense_date: new Date(date).toISOString(),
notes: notes
"""
class ExpenseBase(BaseModel):
    name: str
    category: ExpenseCategory
    amount: float
    expense_date: datetime.datetime
    site_id: Optional[UUID] = None
    notes: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    pass

class SiteBasicInfo(BaseModel):
    id: UUID
    name: str
    code: Optional[str] = None
    
    class Config:
        from_attributes = True

class ExpenseResponse(ExpenseBase):
    id: UUID
    created_at: datetime.datetime
    created_by_id: Optional[UUID] = None
    site: Optional[SiteBasicInfo] = None
    has_evidence: bool = False
    

    class Config:
        from_attributes = True

class ExpenseEvidenceResponse(BaseModel):
    id: UUID
    file_name: str
    file_type: str
    file_url: Optional[str] = None   # URL en Supabase Storage
    file_data: Optional[str] = None  # Legacy: Base64 (solo para registros antiguos)

    class Config:
        from_attributes = True

@router.post("/", response_model=ExpenseResponse)
async def create_expense(
    expense_data: ExpenseBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
): 

    # Verificar si el sitio existe si se proporciona site_id
    if expense_data.site_id:
        site = db.query(Site).filter(Site.id == expense_data.site_id).first()
        if not site:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Site with ID {expense_data.site_id} not found"
            )
   
    # Crear nuevo gasto
    new_expense = OperationalExpense(
        name=expense_data.name,
        category=expense_data.category,
        amount=expense_data.amount,
        expense_date=expense_data.expense_date,
        site_id=expense_data.site_id,
        notes=expense_data.notes,
        created_by_id=current_user.id
    )
    
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    
    return new_expense

@router.get("/", response_model=List[ExpenseResponse])
async def get_expenses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    site_id: Optional[UUID] = None
):
    query = db.query(OperationalExpense)
    # Filtrar por sitio si se proporciona site_id
    if site_id:
        query = query.filter(OperationalExpense.site_id == site_id)
        print(query)
    # Ordenar por fecha del gasto (más reciente primero)
    expenses = query.order_by(OperationalExpense.expense_date.desc()).all()
    return expenses

@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = db.query(OperationalExpense).filter(OperationalExpense.id == expense_id).first()
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with ID {expense_id} not found"
        )
    
    return expense

@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = db.query(OperationalExpense).filter(OperationalExpense.id == expense_id).first()
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with ID {expense_id} not found"
        )
    
    # Eliminar el gasto (las evidencias se eliminarán automáticamente por la cascade)
    db.delete(expense)
    db.commit()
    
    return None

@router.get("/evidence_by_id/{expense_id}", response_model=ExpenseEvidenceResponse)
async def get_expense_evidence(
    expense_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener la evidencia de un gasto específico"""
    
    # Verificar si el gasto existe
    expense = db.query(OperationalExpense).filter(OperationalExpense.id == expense_id).first()
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gasto con ID {expense_id} no encontrado"
        )
    
    # Verificar si el gasto tiene evidencia
    evidence = db.query(ExpenseEvidence).filter(ExpenseEvidence.expense_id == expense_id).first()
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró evidencia para este gasto"
        )

    # Generar signed URL si el registro tiene path en file_url
    file_url = None
    if evidence.file_url and not evidence.file_url.startswith("http"):
        try:
            file_url = create_signed_url(BUCKETS["gastos"], evidence.file_url)
        except Exception:
            file_url = None
    else:
        file_url = evidence.file_url  # legacy: ya era una URL completa

    return ExpenseEvidenceResponse(
        id=evidence.id,
        file_name=evidence.file_name,
        file_type=evidence.file_type,
        file_url=file_url,
        file_data=evidence.file_data,
    )

@router.post("/evidence/{expense_id}")
async def upload_expense_evidence(
    expense_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Subir evidencia para un gasto a Supabase Storage"""
    expense = db.query(OperationalExpense).filter(OperationalExpense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Gasto {expense_id} no encontrado")

    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="El archivo excede el límite de 10MB.")

    content_type = file.content_type or "application/octet-stream"
    path = upload_file(
        bucket=BUCKETS["gastos"],
        file_bytes=file_bytes,
        filename=file.filename,
        content_type=content_type,
        folder=str(expense_id),
    )
    signed_url = create_signed_url(BUCKETS["gastos"], path)

    existing = db.query(ExpenseEvidence).filter(ExpenseEvidence.expense_id == expense_id).first()
    if existing:
        if existing.file_url:
            delete_file(BUCKETS["gastos"], existing.file_url)
        existing.file_name = file.filename
        existing.file_type = content_type
        existing.file_url = path  # guardamos el path, no la URL
        existing.file_data = None
        existing.uploaded_by_id = current_user.id
    else:
        db.add(ExpenseEvidence(
            expense_id=expense_id,
            file_name=file.filename,
            file_type=content_type,
            file_url=path,  # guardamos el path, no la URL
            uploaded_by_id=current_user.id,
        ))

    expense.has_evidence = True
    db.commit()
    return {"message": "Evidencia cargada exitosamente", "url": signed_url}

@router.delete("/evidence/{expense_id}")
async def delete_expense_evidence(
    expense_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar la evidencia de un gasto específico"""
    
    # Verificar si el gasto existe
    expense = db.query(OperationalExpense).filter(OperationalExpense.id == expense_id).first()
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Gasto con ID {expense_id} no encontrado"
        )
    
    # Verificar si el gasto tiene evidencia
    evidence = db.query(ExpenseEvidence).filter(ExpenseEvidence.expense_id == expense_id).first()
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró evidencia para este gasto"
        )
    
    # Eliminar archivo de Storage si existe
    if evidence.file_url:
        delete_file(BUCKETS["gastos"], evidence.file_url)

    db.delete(evidence)

    remaining_evidence = db.query(ExpenseEvidence).filter(ExpenseEvidence.expense_id == expense_id).count()
    if remaining_evidence == 0:
        expense.has_evidence = False

    db.commit()
    return {"message": "Evidencia eliminada exitosamente"}
