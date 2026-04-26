from typing import List, Dict, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import uuid

from db.database import get_db
from auth.utils import get_current_user
from models import User
from . import schemas
from services.acl_service import (
    get_user_permissions_logic,
    get_roles_logic,
    get_modules_logic,
    get_role_permissions_logic,
    update_role_permissions_logic,
    assign_user_role_logic,
    check_permission_logic
)

router = APIRouter()

@router.get("/user-permissions", response_model=schemas.UserPermissions)
async def get_user_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user permissions"""
    return get_user_permissions_logic(db, current_user.id)

@router.get("/roles", response_model=List[schemas.RoleInfo])
async def get_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all roles (admin only)"""
    return get_roles_logic(db, current_user.id)

@router.get("/modules", response_model=List[schemas.ModuleInfo])
async def get_modules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):  
    """Get all modules (admin only)"""
    return get_modules_logic(db, current_user.id)

@router.get("/roles/{role_id}/permissions", response_model=List[schemas.RoleModulePermission])
async def get_role_permissions(
    role_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get permissions for a specific role (admin only)"""
    return get_role_permissions_logic(db, role_id, current_user.id)

@router.put("/roles/{role_id}/permissions")
async def update_role_permissions(
    role_id: uuid.UUID,
    permissions: List[Dict[str, Any]],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update permissions for a role (admin only)"""
    return update_role_permissions_logic(db, role_id, permissions, current_user.id)

@router.put("/users/{user_id}/role")
async def assign_user_role(
    user_id: uuid.UUID,
    role_assignment: schemas.RoleAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign role to user (admin only)"""
    return assign_user_role_logic(db, user_id, role_assignment, current_user.id)

@router.get("/check-permission", response_model=schemas.PermissionCheck)
async def check_permission(
    module_name: str = Query(..., description="Module name to check"),
    permission_type: str = Query(..., description="Permission type (create, read, update, delete, approve, export)"),
    user_id: Optional[uuid.UUID] = Query(None, description="User ID (defaults to current user)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if user has specific permission"""
    target_user_id = user_id if user_id else current_user.id
    return check_permission_logic(db, target_user_id, module_name, permission_type)