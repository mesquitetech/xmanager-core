from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid
from datetime import datetime

from db.database import get_db
from models import AccessLog, Site, User, UserRole
from auth.utils import get_current_user, check_role
from . import schemas

router = APIRouter()

# Get all access logs with pagination
@router.get("/", response_model=schemas.AccessLogList)
async def get_access_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    site_id: Optional[uuid.UUID] = None,
    user_id: Optional[uuid.UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_role([UserRole.ADMINISTRADOR, UserRole.OPERATIVO, UserRole.OPERATIVO]))
):
    # Base query with joins to get user and site information
    query = db.query(
        AccessLog,
        User.full_name.label('user_name'),
        User.email.label('user_email'),
        Site.name.label('site_name'),
        Site.code.label('site_code')
    ).join(
        User, AccessLog.user_id == User.id
    ).join(
        Site, AccessLog.site_id == Site.id
    )
    
    # Apply filters
    if site_id:
        query = query.filter(AccessLog.site_id == site_id)
    
    if user_id:
        query = query.filter(AccessLog.user_id == user_id)
    
    if start_date:
        query = query.filter(AccessLog.check_in_time >= start_date)
    
    if end_date:
        query = query.filter(AccessLog.check_in_time <= end_date)
    
    # Count total records for pagination
    total = query.count()
    
    # Apply pagination
    results = query.order_by(AccessLog.check_in_time.desc()).offset(skip).limit(limit).all()
    
    # Process results to include joined data
    access_logs = []
    for access_log, user_name, user_email, site_name, site_code in results:
        access_log_dict = {
            **access_log.__dict__,
            "user_name": user_name,
            "user_email": user_email,
            "site_name": site_name,
            "site_code": site_code
        }
        # Remove SQLAlchemy state
        if "_sa_instance_state" in access_log_dict:
            del access_log_dict["_sa_instance_state"]
        access_logs.append(access_log_dict)
    
    # Calculate total pages
    pages = (total + limit - 1) // limit
    
    return {
        "items": access_logs,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": pages
    }

# Get access log by ID
@router.get("/{access_log_id}", response_model=schemas.AccessLog)
async def get_access_log(
    access_log_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_role([UserRole.ADMINISTRADOR, UserRole.OPERATIVO, UserRole.OPERATIVO]))
):
    # Query with joins to get user and site information
    result = db.query(
        AccessLog,
        User.full_name.label('user_name'),
        User.email.label('user_email'),
        Site.name.label('site_name'),
        Site.code.label('site_code')
    ).join(
        User, AccessLog.user_id == User.id
    ).join(
        Site, AccessLog.site_id == Site.id
    ).filter(
        AccessLog.id == access_log_id
    ).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Access log not found")
    
    access_log, user_name, user_email, site_name, site_code = result
    
    # Combine data
    access_log_dict = {
        **access_log.__dict__,
        "user_name": user_name,
        "user_email": user_email,
        "site_name": site_name,
        "site_code": site_code
    }
    
    # Remove SQLAlchemy state
    if "_sa_instance_state" in access_log_dict:
        del access_log_dict["_sa_instance_state"]
    
    return access_log_dict

# Create check-in (start access log)
@router.post("/check-in", response_model=schemas.AccessLog, status_code=status.HTTP_201_CREATED)
async def check_in(
    data: schemas.AccessLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify site exists
    site = db.query(Site).filter(Site.id == data.site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    # Check if user already has an open check-in
    open_access = db.query(AccessLog).filter(
        AccessLog.user_id == current_user.id,
        AccessLog.site_id == data.site_id,
        AccessLog.check_out_time == None
    ).first()
    
    if open_access:
        raise HTTPException(status_code=400, detail="You already have an open check-in at this site")
    
    # Create new access log
    new_access_log = AccessLog(
        site_id=data.site_id,
        user_id=current_user.id,
        check_in_time=data.check_in_time,
        check_out_time=data.check_out_time,
        purpose=data.purpose,
        activities=data.activities,
        photos=data.photos,
        notes=data.notes
    )
    
    db.add(new_access_log)
    db.commit()
    db.refresh(new_access_log)
    
    # Add user and site information to response
    result = {
        **new_access_log.__dict__,
        "user_name": current_user.full_name,
        "user_email": current_user.email,
        "site_name": site.name,
        "site_code": site.code
    }
    
    # Remove SQLAlchemy state
    if "_sa_instance_state" in result:
        del result["_sa_instance_state"]
    
    return result

# Update access log (check-out)
@router.put("/{access_log_id}/check-out", response_model=schemas.AccessLog)
async def check_out(
    access_log_id: uuid.UUID,
    data: schemas.AccessLogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get access log
    access_log = db.query(AccessLog).filter(AccessLog.id == access_log_id).first()
    if not access_log:
        raise HTTPException(status_code=404, detail="Access log not found")
    
    # Verify ownership or admin/NOC role
    if access_log.user_id != current_user.id and current_user.role not in [UserRole.ADMINISTRADOR, UserRole.OPERATIVO]:
        raise HTTPException(status_code=403, detail="Not authorized to update this access log")
    
    # Verify check-out time is not already set
    if access_log.check_out_time is not None:
        raise HTTPException(status_code=400, detail="Check-out already completed for this access log")
    
    # Update access log
    for key, value in data.dict(exclude_unset=True).items():
        setattr(access_log, key, value)
    
    access_log.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(access_log)
    
    # Get site and user info for response
    site = db.query(Site).filter(Site.id == access_log.site_id).first()
    user = db.query(User).filter(User.id == access_log.user_id).first()
    
    # Add user and site information to response
    result = {
        **access_log.__dict__,
        "user_name": user.full_name,
        "user_email": user.email,
        "site_name": site.name,
        "site_code": site.code
    }
    
    # Remove SQLAlchemy state
    if "_sa_instance_state" in result:
        del result["_sa_instance_state"]
    
    return result

# Delete access log
@router.delete("/{access_log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_access_log(
    access_log_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_role([UserRole.ADMINISTRADOR, UserRole.OPERATIVO]))
):
    access_log = db.query(AccessLog).filter(AccessLog.id == access_log_id).first()
    if not access_log:
        raise HTTPException(status_code=404, detail="Access log not found")
    
    db.delete(access_log)
    db.commit()
    
    return {"status": "success"}

# Get active check-ins (open access logs)
@router.get("/active", response_model=List[schemas.AccessLog])
async def get_active_check_ins(
    site_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_role([UserRole.ADMINISTRADOR, UserRole.OPERATIVO, UserRole.OPERATIVO]))
):
    # Base query with joins
    query = db.query(
        AccessLog,
        User.full_name.label('user_name'),
        User.email.label('user_email'),
        Site.name.label('site_name'),
        Site.code.label('site_code')
    ).join(
        User, AccessLog.user_id == User.id
    ).join(
        Site, AccessLog.site_id == Site.id
    ).filter(
        AccessLog.check_out_time == None
    )
    
    # Filter by site if specified
    if site_id:
        query = query.filter(AccessLog.site_id == site_id)
    
    results = query.order_by(AccessLog.check_in_time.desc()).all()
    
    # Process results
    active_logs = []
    for access_log, user_name, user_email, site_name, site_code in results:
        access_log_dict = {
            **access_log.__dict__,
            "user_name": user_name,
            "user_email": user_email,
            "site_name": site_name,
            "site_code": site_code
        }
        # Remove SQLAlchemy state
        if "_sa_instance_state" in access_log_dict:
            del access_log_dict["_sa_instance_state"]
        active_logs.append(access_log_dict)
    
    return active_logs

# Get user's active check-in
@router.get("/my-active", response_model=Optional[schemas.AccessLog])
async def get_my_active_check_in(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get user's active check-in
    result = db.query(
        AccessLog,
        Site.name.label('site_name'),
        Site.code.label('site_code')
    ).join(
        Site, AccessLog.site_id == Site.id
    ).filter(
        AccessLog.user_id == current_user.id,
        AccessLog.check_out_time == None
    ).first()
    
    if not result:
        return None
    
    access_log, site_name, site_code = result
    
    # Combine data
    access_log_dict = {
        **access_log.__dict__,
        "user_name": current_user.full_name,
        "user_email": current_user.email,
        "site_name": site_name,
        "site_code": site_code
    }
    
    # Remove SQLAlchemy state
    if "_sa_instance_state" in access_log_dict:
        del access_log_dict["_sa_instance_state"]
    
    return access_log_dict
