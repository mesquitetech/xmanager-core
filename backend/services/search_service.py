"""
Service for search module - handles business logic
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from repositories.search_repository import SearchRepository
from api.search.schemas import (
    SiteSearchRequestCreate, 
    SiteSearchRequestUpdate,
    SiteCandidateCreate,
    SiteCandidateUpdate
)


class SearchService:
    """Service for managing search requests and candidates business logic"""
    
    def __init__(self, db: Session):
        self.repository = SearchRepository(db)
    
    def get_search_requests_paginated(
        self,
        skip: int,
        limit: int,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get paginated search requests with candidates and requester names"""
        # Get results from repository
        results, total = self.repository.get_search_requests_with_pagination(
            skip, limit, status
        )
        
        # Process results to include candidates and clean data
        search_requests = []
        for sr, requester_name in results:
            # Get candidates for each search request
            candidates = self.repository.get_candidates_by_search_request_id(sr.id)
            
            # Build response dictionary
            sr_dict = self._build_search_request_dict(sr, requester_name, candidates)
            search_requests.append(sr_dict)
        
        # Calculate pagination info
        pages = (total + limit - 1) // limit
        
        return {
            "items": search_requests,
            "total": total,
            "page": skip // limit + 1,
            "size": limit,
            "pages": pages
        }
    
    def get_search_request_by_id(self, request_id: UUID) -> Optional[Dict[str, Any]]:
        """Get search request by ID with complete information"""
        # Get search request with requester name
        result = self.repository.get_search_request_by_id_with_requester(request_id)
        
        if not result:
            return None
        
        sr, requester_name = result
        
        # Get candidates
        candidates = self.repository.get_candidates_by_search_request_id(sr.id)
        
        return self._build_search_request_dict(sr, requester_name, candidates or [])
    
    def create_search_request(
        self,
        sr_data: SiteSearchRequestCreate,
        user_id: str
    ) -> Dict[str, Any]:
        """Create a new search request with validation"""
        # Validate business rules
        self._validate_search_request_data(sr_data.dict())
        
        # Create search request
        new_sr = self.repository.create_search_request(sr_data.dict(), user_id)
        
        # Get complete data for response
        return self.get_search_request_by_id(new_sr.id)
    
    def update_search_request(
        self,
        request_id: UUID,
        update_data: SiteSearchRequestUpdate
    ) -> Optional[Dict[str, Any]]:
        """Update search request with validation"""
        # Validate update data
        update_dict = update_data.dict(exclude_unset=True)
        if update_dict:
            self._validate_search_request_data(update_dict, is_update=True)
        
        # Update search request
        updated_sr = self.repository.update_search_request(request_id, update_dict)
        
        if not updated_sr:
            return None
        
        # Return updated data
        return self.get_search_request_by_id(request_id)
    
    def delete_search_request(self, request_id: UUID) -> bool:
        """Delete search request with validation"""
        return self.repository.delete_search_request(request_id)
    
    def create_candidate(
        self,
        candidate_data: SiteCandidateCreate
    ) -> Optional[Dict[str, Any]]:
        """Create a new site candidate with validation"""
        # Validate candidate data
        self._validate_candidate_data(candidate_data.dict())
        
        # Create candidate
        new_candidate = self.repository.create_candidate(candidate_data.dict())
        
        # Return candidate data as dict
        return self._build_candidate_dict(new_candidate)
    
    def update_candidate(
        self,
        candidate_id: UUID,
        update_data: SiteCandidateUpdate
    ) -> Optional[Dict[str, Any]]:
        """Update site candidate with validation"""
        # Validate update data
        update_dict = update_data.dict(exclude_unset=True)
        if update_dict:
            self._validate_candidate_data(update_dict, is_update=True)
        
        # Update candidate
        updated_candidate = self.repository.update_candidate(candidate_id, update_dict)
        
        if not updated_candidate:
            return None
        
        return self._build_candidate_dict(updated_candidate)
    
    def delete_candidate(self, candidate_id: UUID) -> bool:
        """Delete site candidate"""
        return self.repository.delete_candidate(candidate_id)
    
    def get_candidate_by_id(self, candidate_id: UUID) -> Optional[Dict[str, Any]]:
        """Get candidate by ID"""
        candidate = self.repository.get_candidate_by_id(candidate_id)
        
        if not candidate:
            return None
        
        return self._build_candidate_dict(candidate)
    
    def search_requests_by_criteria(
        self,
        city: Optional[str] = None,
        state: Optional[str] = None,
        country: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search requests by multiple criteria"""
        results = self.repository.search_requests_by_criteria(
            city, state, country, status, priority
        )
        
        # Build response with basic info (no candidates for performance)
        search_requests = []
        for sr in results:
            sr_dict = self._build_basic_search_request_dict(sr)
            search_requests.append(sr_dict)
        
        return search_requests
    
    def _build_search_request_dict(
        self, sr, requester_name: str, candidates: List = None
    ) -> Dict[str, Any]:
        """Build search request dictionary with complete information"""
        sr_dict = {
            **sr.__dict__,
            "requested_by_name": requester_name,
            "candidates": [self._build_candidate_dict(c) for c in (candidates or [])]
        }
        
        # Remove SQLAlchemy state
        if "_sa_instance_state" in sr_dict:
            del sr_dict["_sa_instance_state"]
        
        # Convert datetime objects to ISO format
        if hasattr(sr, 'created_at') and sr.created_at:
            sr_dict["created_at"] = sr.created_at.isoformat()
        if hasattr(sr, 'updated_at') and sr.updated_at:
            sr_dict["updated_at"] = sr.updated_at.isoformat()
        if hasattr(sr, 'due_date') and sr.due_date:
            sr_dict["due_date"] = sr.due_date.isoformat()
        
        return sr_dict
    
    def _build_basic_search_request_dict(self, sr) -> Dict[str, Any]:
        """Build basic search request dictionary without candidates"""
        sr_dict = {**sr.__dict__}
        
        # Remove SQLAlchemy state
        if "_sa_instance_state" in sr_dict:
            del sr_dict["_sa_instance_state"]
        
        # Convert datetime objects
        if hasattr(sr, 'created_at') and sr.created_at:
            sr_dict["created_at"] = sr.created_at.isoformat()
        if hasattr(sr, 'updated_at') and sr.updated_at:
            sr_dict["updated_at"] = sr.updated_at.isoformat()
        
        return sr_dict
    
    def _build_candidate_dict(self, candidate) -> Dict[str, Any]:
        """Build candidate dictionary"""
        candidate_dict = {**candidate.__dict__}
        
        # Remove SQLAlchemy state
        if "_sa_instance_state" in candidate_dict:
            del candidate_dict["_sa_instance_state"]
        
        # Convert datetime objects
        if hasattr(candidate, 'created_at') and candidate.created_at:
            candidate_dict["created_at"] = candidate.created_at.isoformat()
        if hasattr(candidate, 'updated_at') and candidate.updated_at:
            candidate_dict["updated_at"] = candidate.updated_at.isoformat()
        
        return candidate_dict
    
    def _validate_search_request_data(self, data: Dict[str, Any], is_update: bool = False):
        """Validate search request data according to business rules"""
        if not is_update and not data.get('title'):
            raise ValueError("Title is required for search requests")
        
        # Validate coordinates if provided
        if 'target_latitude' in data and 'target_longitude' in data:
            lat = data['target_latitude']
            lng = data['target_longitude']
            if lat is not None and lng is not None:
                if not (-90 <= lat <= 90):
                    raise ValueError("Latitude must be between -90 and 90")
                if not (-180 <= lng <= 180):
                    raise ValueError("Longitude must be between -180 and 180")
        
        # Validate budget range
        if 'budget_min' in data and 'budget_max' in data:
            budget_min = data['budget_min']
            budget_max = data['budget_max']
            if (budget_min is not None and budget_max is not None 
                and budget_min > budget_max):
                raise ValueError("Minimum budget cannot be greater than maximum budget")
        
        # Validate status
        valid_statuses = ['new', 'in_progress', 'completed', 'cancelled']
        if 'status' in data and data['status'] not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        
        # Validate priority
        valid_priorities = ['low', 'medium', 'high', 'urgent']
        if 'priority' in data and data['priority'] and data['priority'] not in valid_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")
    
    def _validate_candidate_data(self, data: Dict[str, Any], is_update: bool = False):
        """Validate candidate data according to business rules"""
        if not is_update and not data.get('address'):
            raise ValueError("Address is required for candidates")
        
        # Validate coordinates
        if 'latitude' in data and 'longitude' in data:
            lat = data['latitude']
            lng = data['longitude']
            if not is_update or (lat is not None and lng is not None):
                if not (-90 <= lat <= 90):
                    raise ValueError("Latitude must be between -90 and 90")
                if not (-180 <= lng <= 180):
                    raise ValueError("Longitude must be between -180 and 180")
        
        # Validate rent amount
        if 'estimated_monthly_rent' in data:
            rent = data['estimated_monthly_rent']
            if rent is not None and rent < 0:
                raise ValueError("Estimated monthly rent cannot be negative")
        
        # Validate status
        valid_statuses = ['pending', 'approved', 'rejected', 'contacted']
        if 'status' in data and data['status'] not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")