"""
Router para el módulo de seguros - Solo endpoints HTTP
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import Response, RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from uuid import UUID

from db.database import get_db
from auth.utils import get_current_user
from models import User
from services.seguros_service import SegurosService
from repositories.seguros_repository import SegurosRepository
from utils.storage import upload_file, create_signed_url, delete_file, BUCKETS
from .schemas import (
    SeguroCreate, SeguroUpdate, SeguroResponse,
    SeguroStats, SeguroFilter
)

router = APIRouter(prefix="/api/seguros", tags=["seguros"])

@router.get("/stats", response_model=SeguroStats)
async def get_seguros_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener estadísticas de seguros"""
    try:
        return SegurosService.get_stats(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")

@router.get("/", response_model=List[SeguroResponse])
async def get_seguros(
    search: Optional[str] = None,
    estado: Optional[str] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    site_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener lista de seguros con filtros"""
    try:
        return SegurosService.get_seguros_list(
            db=db,
            search=search,
            estado=estado,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            site_id=site_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener seguros: {str(e)}")

@router.post("/", response_model=SeguroResponse)
async def create_seguro(
    seguro_data: SeguroCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear nueva póliza de seguro"""
    try:
        db.begin()
        result = SegurosService.create_seguro(db, seguro_data)
        db.commit()
        return result
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear seguro: {str(e)}")

@router.post("/{seguro_id}/poliza")
async def upload_poliza_file(
    seguro_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Subir archivo de póliza a Supabase Storage"""
    try:
        seguro_db = SegurosRepository.get_seguro_by_id(db, seguro_id)
        if not seguro_db:
            raise HTTPException(status_code=404, detail="Seguro no encontrado")

        # Eliminar archivo anterior si existe
        if seguro_db.poliza_url:
            delete_file(BUCKETS["seguros"], seguro_db.poliza_url)

        file_bytes = await file.read()
        content_type = file.content_type or "application/pdf"
        path = upload_file(
            bucket=BUCKETS["seguros"],
            file_bytes=file_bytes,
            filename=file.filename,
            content_type=content_type,
            folder=f"{seguro_id}/poliza",
        )
        signed_url = create_signed_url(BUCKETS["seguros"], path)

        seguro_db.poliza_filename = file.filename
        seguro_db.poliza_content_type = content_type
        seguro_db.poliza_url = path  # guardamos el path, no la URL
        db.commit()

        return {"url": signed_url, "filename": file.filename}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir póliza: {str(e)}")

@router.get("/{seguro_id}/poliza")
async def get_poliza_file(
    seguro_id: str,
    token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Redirigir a la URL del archivo de póliza en Supabase Storage"""
    try:
        import uuid as uuid_lib
        seguro_uuid = uuid_lib.UUID(seguro_id)
        seguro_db = SegurosRepository.get_seguro_by_id(db, seguro_uuid)
        if not seguro_db:
            raise HTTPException(status_code=404, detail="Seguro no encontrado")

        # Compatibilidad: si aún tiene contenido en DB, servirlo directamente
        if seguro_db.poliza_url:
            signed_url = create_signed_url(BUCKETS["seguros"], seguro_db.poliza_url)
            return RedirectResponse(url=signed_url)
        if seguro_db.poliza_content:
            return Response(
                content=seguro_db.poliza_content,
                media_type=seguro_db.poliza_content_type or "application/pdf",
                headers={"Content-Disposition": f"inline; filename={seguro_db.poliza_filename or 'poliza.pdf'}"}
            )
        raise HTTPException(status_code=404, detail="Archivo de póliza no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener póliza: {str(e)}")

@router.post("/{seguro_id}/contrato")
async def upload_contrato_file(
    seguro_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Subir archivo de contrato a Supabase Storage"""
    try:
        seguro_db = SegurosRepository.get_seguro_by_id(db, seguro_id)
        if not seguro_db:
            raise HTTPException(status_code=404, detail="Seguro no encontrado")

        if seguro_db.contrato_url:
            delete_file(BUCKETS["seguros"], seguro_db.contrato_url)

        file_bytes = await file.read()
        content_type = file.content_type or "application/pdf"
        path = upload_file(
            bucket=BUCKETS["seguros"],
            file_bytes=file_bytes,
            filename=file.filename,
            content_type=content_type,
            folder=f"{seguro_id}/contrato",
        )
        signed_url = create_signed_url(BUCKETS["seguros"], path)

        seguro_db.contrato_filename = file.filename
        seguro_db.contrato_content_type = content_type
        seguro_db.contrato_url = path  # guardamos el path, no la URL
        db.commit()

        return {"url": signed_url, "filename": file.filename}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir contrato: {str(e)}")

@router.get("/{seguro_id}/contrato")
async def get_contrato_file(
    seguro_id: str,
    token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Redirigir a la URL del archivo de contrato en Supabase Storage"""
    try:
        import uuid as uuid_lib
        seguro_uuid = uuid_lib.UUID(seguro_id)
        seguro_db = SegurosRepository.get_seguro_by_id(db, seguro_uuid)
        if not seguro_db:
            raise HTTPException(status_code=404, detail="Seguro no encontrado")

        if seguro_db.contrato_url:
            signed_url = create_signed_url(BUCKETS["seguros"], seguro_db.contrato_url)
            return RedirectResponse(url=signed_url)
        if seguro_db.contrato_content:
            return Response(
                content=seguro_db.contrato_content,
                media_type=seguro_db.contrato_content_type or "application/pdf",
                headers={"Content-Disposition": f"inline; filename={seguro_db.contrato_filename or 'contrato.pdf'}"}
            )
        raise HTTPException(status_code=404, detail="Archivo de contrato no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener contrato: {str(e)}")

@router.put("/{seguro_id}", response_model=SeguroResponse)
async def update_seguro(
    seguro_id: UUID,
    seguro_data: SeguroUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar póliza de seguro"""
    try:
        db.begin()
        result = SegurosService.update_seguro(db, seguro_id, seguro_data)
        if not result:
            raise HTTPException(status_code=404, detail="Seguro no encontrado")
        db.commit()
        return result
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar seguro: {str(e)}")

@router.delete("/{seguro_id}")
async def delete_seguro(
    seguro_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar póliza de seguro"""
    try:
        db.begin()
        success = SegurosService.delete_seguro(db, seguro_id)
        if not success:
            raise HTTPException(status_code=404, detail="Seguro no encontrado")
        db.commit()
        return {"message": "Seguro eliminado exitosamente"}
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar seguro: {str(e)}")