from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime

from repositories.incident_repository import (
    get_incidents_with_pagination,
    get_incident_by_id,
    create_incident_in_db,
    update_incident_in_db,
    delete_incident_from_db,
    assign_incident_in_db,
    get_site_by_id,
    get_user_by_id,
    get_assignee_name
)
from models import User, UserRole, IncidentStatus, IncidentPriority
from api.incidents.schemas import IncidentCreate, IncidentUpdate


def get_incidents_logic(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    site_id: Optional[uuid.UUID] = None,
    status: Optional[IncidentStatus] = None,
    priority: Optional[IncidentPriority] = None,
    category: Optional[str] = None,
    assignee_id: Optional[uuid.UUID] = None
) -> Dict[str, Any]:
    """Business logic for getting incidents with pagination"""
    
    try:
        results, total = get_incidents_with_pagination(
            db, skip, limit, site_id, status, priority, category, assignee_id
        )
        
        # Process results to include joined data
        incidents = []
        for incident, site_name, site_code, reporter_name in results:
            # Get assignee name if applicable
            assignee_name = None
            if incident.assignee_id:
                assignee_name = get_assignee_name(db, incident.assignee_id)
            
            incident_dict = {
                **incident.__dict__,
                "site_name": site_name,
                "site_code": site_code,
                "reporter_name": reporter_name,
                "assignee_name": assignee_name
            }
            # Remove SQLAlchemy state
            if "_sa_instance_state" in incident_dict:
                del incident_dict["_sa_instance_state"]
            incidents.append(incident_dict)
        
        # Calculate total pages
        pages = (total + limit - 1) // limit
        
        return {
            "items": incidents,
            "total": total,
            "page": skip // limit + 1,
            "size": limit,
            "pages": pages
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving incidents: {str(e)}")


def get_incident_logic(db: Session, incident_id: uuid.UUID) -> Dict[str, Any]:
    """Business logic for getting single incident"""
    
    try:
        result = get_incident_by_id(db, incident_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        incident, site_name, site_code, reporter_name = result
        
        # Get assignee name if applicable
        assignee_name = None
        if incident.assignee_id:
            assignee_name = get_assignee_name(db, incident.assignee_id)
        
        # Combine data
        incident_dict = {
            **incident.__dict__,
            "site_name": site_name,
            "site_code": site_code,
            "reporter_name": reporter_name,
            "assignee_name": assignee_name
        }
        
        # Remove SQLAlchemy state
        if "_sa_instance_state" in incident_dict:
            del incident_dict["_sa_instance_state"]
        
        return incident_dict
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving incident: {str(e)}")


def create_incident_logic(
    db: Session, 
    incident_data: IncidentCreate, 
    current_user: User
) -> Dict[str, Any]:
    """Business logic for creating new incident"""
    
    try:
        # Verify site exists
        site = get_site_by_id(db, incident_data.site_id)
        if not site:
            raise HTTPException(status_code=404, detail="Site not found")
        
        # Create new incident
        incident_dict = incident_data.dict()
        new_incident = create_incident_in_db(db, incident_dict, current_user.id)
        
        # Add site and user information for response
        result = {
            **new_incident.__dict__,
            "site_name": site.name,
            "site_code": site.code,
            "reporter_name": current_user.full_name,
            "assignee_name": None
        }
        
        # Remove SQLAlchemy state
        if "_sa_instance_state" in result:
            del result["_sa_instance_state"]
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating incident: {str(e)}")


def update_incident_logic(
    db: Session,
    incident_id: uuid.UUID,
    incident_data: IncidentUpdate,
    current_user: User
) -> Dict[str, Any]:
    """Business logic for updating incident"""
    
    try:
        # Get incident
        result = get_incident_by_id(db, incident_id)
        if not result:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        incident, _, _, _ = result
        
        # Check permissions - either the reporter, assignee, or admin/NOC can update
        if (incident.reporter_id != current_user.id 
            and incident.assignee_id != current_user.id 
            and current_user.role not in [UserRole.ADMINISTRADOR, UserRole.OPERATIVO]):
            raise HTTPException(status_code=403, detail="Not authorized to update this incident")
        
        # Update incident
        update_data = incident_data.dict(exclude_unset=True)
        updated_incident = update_incident_in_db(db, incident, update_data)
        
        # Get related data for response
        site = get_site_by_id(db, updated_incident.site_id)
        reporter = get_user_by_id(db, updated_incident.reporter_id)
        
        assignee_name = None
        if updated_incident.assignee_id:
            assignee_name = get_assignee_name(db, updated_incident.assignee_id)
        
        # Combine data
        result = {
            **updated_incident.__dict__,
            "site_name": site.name if site else None,
            "site_code": site.code if site else None,
            "reporter_name": reporter.full_name if reporter else None,
            "assignee_name": assignee_name
        }
        
        # Remove SQLAlchemy state
        if "_sa_instance_state" in result:
            del result["_sa_instance_state"]
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating incident: {str(e)}")


def delete_incident_logic(db: Session, incident_id: uuid.UUID) -> Dict[str, str]:
    """Business logic for deleting incident"""
    
    try:
        result = get_incident_by_id(db, incident_id)
        if not result:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        incident, _, _, _ = result
        delete_incident_from_db(db, incident)
        
        return {"status": "success"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting incident: {str(e)}")


def assign_incident_logic(
    db: Session,
    incident_id: uuid.UUID,
    assignee_id: uuid.UUID
) -> Dict[str, Any]:
    """Business logic for assigning incident"""
    
    try:
        # Get incident
        result = get_incident_by_id(db, incident_id)
        if not result:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        incident, _, _, _ = result
        
        # Verify assignee exists
        assignee = get_user_by_id(db, assignee_id)
        if not assignee:
            raise HTTPException(status_code=404, detail="Assignee not found")
        
        # Update incident
        updated_incident = assign_incident_in_db(db, incident, assignee_id)
        
        # Get related data for response
        site = get_site_by_id(db, updated_incident.site_id)
        reporter = get_user_by_id(db, updated_incident.reporter_id)
        
        # Combine data
        result = {
            **updated_incident.__dict__,
            "site_name": site.name if site else None,
            "site_code": site.code if site else None,
            "reporter_name": reporter.full_name if reporter else None,
            "assignee_name": assignee.full_name
        }
        
        # Remove SQLAlchemy state
        if "_sa_instance_state" in result:
            del result["_sa_instance_state"]
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error assigning incident: {str(e)}")