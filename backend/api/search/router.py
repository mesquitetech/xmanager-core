"""
Router for search module - handles HTTP endpoints only (Clean Architecture)
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from db.database import get_db
from models import User, UserRole
from auth.utils import get_current_user, check_role
from services.search_service import SearchService
from . import schemas

router = APIRouter()


@router.get("/requests", response_model=schemas.SiteSearchRequestList)
async def get_search_requests(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_role([UserRole.ADMINISTRADOR, UserRole.FINANCIERO, UserRole.OPERATIVO]))
):
    """Get all search requests with pagination"""
    try:
        service = SearchService(db)
        result = service.get_search_requests_paginated(skip, limit, status)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/requests/{request_id}", response_model=schemas.SiteSearchRequest)
async def get_search_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_role([UserRole.ADMINISTRADOR, UserRole.FINANCIERO, UserRole.OPERATIVO]))
):
    """Get search request by ID"""
    try:
        service = SearchService(db)
        result = service.get_search_request_by_id(request_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Search request not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/requests", response_model=schemas.SiteSearchRequest, status_code=status.HTTP_201_CREATED)
async def create_search_request(
    sr_data: schemas.SiteSearchRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_role([UserRole.ADMINISTRADOR, UserRole.FINANCIERO, UserRole.OPERATIVO]))
):
    """Create new search request"""
    try:
        service = SearchService(db)
        result = service.create_search_request(sr_data, str(current_user.id))
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/requests/{request_id}", response_model=schemas.SiteSearchRequest)
async def update_search_request(
    request_id: UUID,
    sr_data: schemas.SiteSearchRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_role([UserRole.ADMINISTRADOR, UserRole.FINANCIERO, UserRole.OPERATIVO]))
):
    """Update search request"""
    try:
        service = SearchService(db)
        result = service.update_search_request(request_id, sr_data)
        
        if not result:
            raise HTTPException(status_code=404, detail="Search request not found")
        
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_search_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_role([UserRole.ADMINISTRADOR]))
):
    """Delete search request"""
    try:
        service = SearchService(db)
        success = service.delete_search_request(request_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Search request not found")
        
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/candidates", response_model=schemas.SiteCandidate, status_code=status.HTTP_201_CREATED)
async def add_candidate(
    candidate_data: schemas.SiteCandidateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_role([UserRole.ADMINISTRADOR, UserRole.FINANCIERO, UserRole.OPERATIVO]))
):
    """Add candidate to search request"""
    try:
        service = SearchService(db)
        result = service.create_candidate(candidate_data)
        
        if not result:
            raise HTTPException(status_code=404, detail="Search request not found")
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/candidates/{candidate_id}", response_model=schemas.SiteCandidate)
async def get_candidate(
    candidate_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_role([UserRole.ADMINISTRADOR, UserRole.FINANCIERO, UserRole.OPERATIVO]))
):
    """Get candidate by ID"""
    try:
        service = SearchService(db)
        result = service.get_candidate_by_id(candidate_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/candidates/{candidate_id}", response_model=schemas.SiteCandidate)
async def update_candidate(
    candidate_id: UUID,
    candidate_data: schemas.SiteCandidateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_role([UserRole.ADMINISTRADOR, UserRole.FINANCIERO, UserRole.OPERATIVO]))
):
    """Update candidate"""
    try:
        service = SearchService(db)
        result = service.update_candidate(candidate_id, candidate_data)
        
        if not result:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/candidates/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(
    candidate_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_role([UserRole.ADMINISTRADOR, UserRole.FINANCIERO, UserRole.OPERATIVO]))
):
    """Delete candidate"""
    try:
        service = SearchService(db)
        success = service.delete_candidate(candidate_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/requests/{request_id}/candidates", response_model=List[schemas.SiteCandidate])
async def get_candidates_for_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_role([UserRole.ADMINISTRADOR, UserRole.FINANCIERO, UserRole.OPERATIVO]))
):
    """Get candidates for a search request"""
    try:
        service = SearchService(db)
        
        # First verify search request exists
        sr = service.get_search_request_by_id(request_id)
        if not sr:
            raise HTTPException(status_code=404, detail="Search request not found")
        
        # Return candidates from the search request
        return sr.get("candidates", [])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=List[schemas.SiteSearchRequest])
async def search_requests(
    city: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_role([UserRole.ADMINISTRADOR, UserRole.FINANCIERO, UserRole.OPERATIVO]))
):
    """Search requests by multiple criteria"""
    try:
        service = SearchService(db)
        results = service.search_requests_by_criteria(
            city=city,
            state=state,
            country=country,
            status=status,
            priority=priority
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))