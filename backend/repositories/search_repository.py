"""
Repository for search module - handles all database interactions
"""

from typing import List, Optional, Tuple, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from uuid import UUID
from datetime import datetime

from models import SiteSearchRequest, SiteCandidate, User


class SearchRepository:
    """Repository for managing search requests and candidates"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_search_requests_with_pagination(
        self,
        skip: int,
        limit: int,
        status: Optional[str] = None
    ) -> Tuple[List[Any], int]:
        """Get search requests with pagination and requester name"""
        # Base query with join to get requester name
        query = self.db.query(
            SiteSearchRequest,
            User.full_name.label('requested_by_name')
        ).join(
            User, SiteSearchRequest.requested_by_id == User.id
        )
        
        # Apply status filter
        if status:
            query = query.filter(SiteSearchRequest.status == status)
        
        # Count total records for pagination
        total = query.count()
        
        # Apply pagination
        results = query.order_by(SiteSearchRequest.created_at.desc()).offset(skip).limit(limit).all()
        
        return results, total
    
    def get_candidates_by_search_request_id(self, search_request_id: UUID) -> List[SiteCandidate]:
        """Get all candidates for a search request"""
        return self.db.query(SiteCandidate).filter(
            SiteCandidate.search_request_id == search_request_id
        ).all()
    
    def get_search_request_by_id_with_requester(
        self, 
        request_id: UUID
    ) -> Optional[Any]:
        """Get search request by ID with requester name"""
        return self.db.query(
            SiteSearchRequest,
            User.full_name.label('requested_by_name')
        ).join(
            User, SiteSearchRequest.requested_by_id == User.id
        ).filter(
            SiteSearchRequest.id == request_id
        ).first()
    
    def create_search_request(
        self,
        search_request_data: Dict[str, Any],
        user_id: str
    ) -> SiteSearchRequest:
        """Create a new search request"""
        # Create geom point from target coordinates if provided
        geom = None
        if (search_request_data.get('target_latitude') is not None 
            and search_request_data.get('target_longitude') is not None):
            geom = func.ST_SetSRID(
                func.ST_MakePoint(
                    search_request_data['target_longitude'], 
                    search_request_data['target_latitude']
                ),
                4326
            )
        
        # Remove coordinates from data to avoid conflicts
        clean_data = {k: v for k, v in search_request_data.items() 
                     if k not in ['target_latitude', 'target_longitude']}
        
        # Create new search request
        new_sr = SiteSearchRequest(
            **clean_data,
            requested_by_id=user_id,
            target_geom=geom,
            created_at=datetime.now()
        )
        
        self.db.add(new_sr)
        self.db.commit()
        self.db.refresh(new_sr)
        return new_sr
    
    def update_search_request(
        self,
        request_id: UUID,
        update_data: Dict[str, Any]
    ) -> Optional[SiteSearchRequest]:
        """Update a search request"""
        sr = self.db.query(SiteSearchRequest).filter(
            SiteSearchRequest.id == request_id
        ).first()
        
        if not sr:
            return None
        
        # Handle geom update if coordinates provided
        if ('target_latitude' in update_data and 'target_longitude' in update_data
            and update_data['target_latitude'] is not None 
            and update_data['target_longitude'] is not None):
            sr.target_geom = func.ST_SetSRID(
                func.ST_MakePoint(
                    update_data['target_longitude'], 
                    update_data['target_latitude']
                ),
                4326
            )
        
        # Update other fields
        for key, value in update_data.items():
            if key not in ['target_latitude', 'target_longitude'] and hasattr(sr, key):
                setattr(sr, key, value)
        
        sr.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(sr)
        return sr
    
    def delete_search_request(self, request_id: UUID) -> bool:
        """Delete a search request and its candidates"""
        sr = self.db.query(SiteSearchRequest).filter(
            SiteSearchRequest.id == request_id
        ).first()
        
        if not sr:
            return False
        
        # Delete candidates first
        self.db.query(SiteCandidate).filter(
            SiteCandidate.search_request_id == request_id
        ).delete()
        
        # Delete search request
        self.db.delete(sr)
        self.db.commit()
        return True
    
    def get_candidate_by_id(self, candidate_id: UUID) -> Optional[SiteCandidate]:
        """Get candidate by ID"""
        return self.db.query(SiteCandidate).filter(
            SiteCandidate.id == candidate_id
        ).first()
    
    def create_candidate(
        self,
        candidate_data: Dict[str, Any]
    ) -> SiteCandidate:
        """Create a new site candidate"""
        # Create geom point from coordinates if provided
        geom = None
        if (candidate_data.get('latitude') is not None 
            and candidate_data.get('longitude') is not None):
            geom = func.ST_SetSRID(
                func.ST_MakePoint(
                    candidate_data['longitude'], 
                    candidate_data['latitude']
                ),
                4326
            )
        
        # Remove coordinates from data to avoid conflicts
        clean_data = {k: v for k, v in candidate_data.items() 
                     if k not in ['latitude', 'longitude']}
        
        new_candidate = SiteCandidate(
            **clean_data,
            location_geom=geom,
            created_at=datetime.now()
        )
        
        self.db.add(new_candidate)
        self.db.commit()
        self.db.refresh(new_candidate)
        return new_candidate
    
    def update_candidate(
        self,
        candidate_id: UUID,
        update_data: Dict[str, Any]
    ) -> Optional[SiteCandidate]:
        """Update a site candidate"""
        candidate = self.db.query(SiteCandidate).filter(
            SiteCandidate.id == candidate_id
        ).first()
        
        if not candidate:
            return None
        
        # Handle geom update if coordinates provided
        if ('latitude' in update_data and 'longitude' in update_data
            and update_data['latitude'] is not None 
            and update_data['longitude'] is not None):
            candidate.location_geom = func.ST_SetSRID(
                func.ST_MakePoint(
                    update_data['longitude'], 
                    update_data['latitude']
                ),
                4326
            )
        
        # Update other fields
        for key, value in update_data.items():
            if key not in ['latitude', 'longitude'] and hasattr(candidate, key):
                setattr(candidate, key, value)
        
        candidate.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(candidate)
        return candidate
    
    def delete_candidate(self, candidate_id: UUID) -> bool:
        """Delete a site candidate"""
        candidate = self.db.query(SiteCandidate).filter(
            SiteCandidate.id == candidate_id
        ).first()
        
        if not candidate:
            return False
        
        self.db.delete(candidate)
        self.db.commit()
        return True
    
    def search_requests_by_criteria(
        self,
        city: Optional[str] = None,
        state: Optional[str] = None,
        country: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None
    ) -> List[SiteSearchRequest]:
        """Search requests by various criteria"""
        query = self.db.query(SiteSearchRequest)
        
        if city:
            query = query.filter(SiteSearchRequest.city.ilike(f'%{city}%'))
        if state:
            query = query.filter(SiteSearchRequest.state.ilike(f'%{state}%'))
        if country:
            query = query.filter(SiteSearchRequest.country.ilike(f'%{country}%'))
        if status:
            query = query.filter(SiteSearchRequest.status == status)
        if priority:
            query = query.filter(SiteSearchRequest.priority == priority)
        
        return query.order_by(SiteSearchRequest.created_at.desc()).all()