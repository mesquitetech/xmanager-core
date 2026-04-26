from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from models import Incident, Site, User, IncidentStatus, IncidentPriority
from typing import Optional, List, Tuple, Dict, Any
import uuid
from datetime import datetime


def get_incidents_with_pagination(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    site_id: Optional[uuid.UUID] = None,
    status: Optional[IncidentStatus] = None,
    priority: Optional[IncidentPriority] = None,
    category: Optional[str] = None,
    assignee_id: Optional[uuid.UUID] = None
) -> Tuple[List[Tuple], int]:
    """Get incidents with filters and pagination, returns (results, total_count)"""
    
    # Base query with joins
    query = db.query(
        Incident,
        Site.name.label('site_name'),
        Site.code.label('site_code'),
        User.full_name.label('reporter_name')
    ).join(
        Site, Incident.site_id == Site.id
    ).join(
        User, Incident.reporter_id == User.id, isouter=True
    )
    
    # Apply filters
    if site_id:
        query = query.filter(Incident.site_id == site_id)
    
    if status:
        query = query.filter(Incident.status == status)
    
    if priority:
        query = query.filter(Incident.priority == priority)
    
    if category:
        query = query.filter(Incident.category == category)
    
    if assignee_id:
        query = query.filter(Incident.assignee_id == assignee_id)
    
    # Count total records
    total = query.count()
    
    # Apply pagination and ordering
    results = query.order_by(Incident.reported_at.desc()).offset(skip).limit(limit).all()
    
    return results, total


def get_incident_by_id(db: Session, incident_id: uuid.UUID) -> Optional[Tuple]:
    """Get single incident with related data"""
    
    result = db.query(
        Incident,
        Site.name.label('site_name'),
        Site.code.label('site_code'),
        User.full_name.label('reporter_name')
    ).join(
        Site, Incident.site_id == Site.id
    ).join(
        User, Incident.reporter_id == User.id, isouter=True
    ).filter(
        Incident.id == incident_id
    ).first()
    
    return result


def create_incident_in_db(db: Session, incident_data: Dict[str, Any], reporter_id: uuid.UUID) -> Incident:
    """Create new incident in database"""
    
    new_incident = Incident(
        reporter_id=reporter_id,
        status=IncidentStatus.OPEN,
        reported_at=datetime.utcnow(),
        **incident_data
    )
    
    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)
    
    return new_incident


def update_incident_in_db(db: Session, incident: Incident, update_data: Dict[str, Any]) -> Incident:
    """Update incident in database"""
    
    # If status is being changed to RESOLVED, set resolved_at time
    if "status" in update_data and update_data["status"] == IncidentStatus.RESOLVED:
        update_data["resolved_at"] = datetime.utcnow()
    
    # Update fields
    for key, value in update_data.items():
        setattr(incident, key, value)
    
    incident.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(incident)
    
    return incident


def delete_incident_from_db(db: Session, incident: Incident) -> None:
    """Delete incident from database"""
    
    db.delete(incident)
    db.commit()


def assign_incident_in_db(db: Session, incident: Incident, assignee_id: uuid.UUID) -> Incident:
    """Assign incident to user in database"""
    
    incident.assignee_id = assignee_id
    if incident.status == IncidentStatus.OPEN:
        incident.status = IncidentStatus.IN_PROGRESS
    
    incident.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(incident)
    
    return incident


def get_site_by_id(db: Session, site_id: uuid.UUID) -> Optional[Site]:
    """Get site by ID"""
    
    return db.query(Site).filter(Site.id == site_id).first()


def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
    """Get user by ID"""
    
    return db.query(User).filter(User.id == user_id).first()


def get_assignee_name(db: Session, assignee_id: uuid.UUID) -> Optional[str]:
    """Get assignee name by ID"""
    
    assignee = db.query(User).filter(User.id == assignee_id).first()
    return assignee.full_name if assignee else None