"""
Service layer for ACL (Access Control List) operations
Handles business logic and validation for roles, modules, and permissions
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import uuid

from repositories.acl_repository import (
    get_user_role_and_permissions,
    get_all_roles,
    get_all_modules,
    get_role_permissions,
    update_role_permissions,
    assign_user_role,
    check_user_permission,
    get_user_by_id,
    get_role_by_id
)
from api.acl.schemas import (
    UserPermissions,
    RoleInfo,
    ModuleInfo,
    RoleAssignment,
    RoleModulePermission,
    PermissionCheck
)


def get_user_permissions_logic(db: Session, user_id: uuid.UUID) -> UserPermissions:
    """Business logic for getting user permissions"""
    
    # Get user permissions from repository
    permissions_data = get_user_role_and_permissions(db, user_id)
    
    if not permissions_data:
        # Return default permissions for users without roles
        return UserPermissions(
            user_id=user_id,
            role_name="sin_rol",
            role_display_name="Sin Rol",
            modules=[]
        )
    
    return UserPermissions(**permissions_data)


def get_roles_logic(db: Session, current_user_id: uuid.UUID) -> List[RoleInfo]:
    """Business logic for getting all roles (admin only)"""
    
    # Verify user has admin permissions
    has_permission = check_user_permission(db, current_user_id, "users", "read")
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información"
        )
    
    # Get roles from repository
    roles_data = get_all_roles(db)
    
    return [RoleInfo(**role) for role in roles_data]


def get_modules_logic(db: Session, current_user_id: uuid.UUID) -> List[ModuleInfo]:
    """Business logic for getting all modules (admin only)"""
    
    # Verify user has admin permissions
    has_permission = check_user_permission(db, current_user_id, "users", "read")
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información"
        )
    
    # Get modules from repository
    modules_data = get_all_modules(db)
    
    return [ModuleInfo(**module) for module in modules_data]


def get_role_permissions_logic(db: Session, role_id: uuid.UUID, current_user_id: uuid.UUID) -> List[RoleModulePermission]:
    """Business logic for getting role permissions (admin only)"""
    
    # Verify user has admin permissions
    has_permission = check_user_permission(db, current_user_id, "users", "read")
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a esta información"
        )
    
    # Verify role exists
    role = get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    
    # Get role permissions from repository
    permissions_data = get_role_permissions(db, role_id)
    
    return [RoleModulePermission(**permission) for permission in permissions_data]


def update_role_permissions_logic(
    db: Session, 
    role_id: uuid.UUID, 
    permissions: List[Dict[str, Any]], 
    current_user_id: uuid.UUID
) -> Dict[str, str]:
    """Business logic for updating role permissions (admin only)"""
    
    # Verify user has admin permissions
    has_permission = check_user_permission(db, current_user_id, "users", "update")
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para modificar permisos"
        )
    
    # Verify role exists
    role = get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    
    # Validate permissions data
    for permission in permissions:
        if "module_id" not in permission:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="module_id es requerido para cada permiso"
            )
    
    # Update permissions via repository
    success = update_role_permissions(db, role_id, permissions)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar permisos del rol"
        )
    
    return {"message": "Permisos actualizados correctamente"}


def assign_user_role_logic(
    db: Session, 
    user_id: uuid.UUID, 
    role_assignment: RoleAssignment, 
    current_user_id: uuid.UUID
) -> Dict[str, str]:
    """Business logic for assigning role to user (admin only)"""
    
    # Verify user has admin permissions
    has_permission = check_user_permission(db, current_user_id, "users", "update")
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para asignar roles"
        )
    
    # Verify target user exists
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verify role exists
    role = get_role_by_id(db, role_assignment.role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    
    # Assign role via repository
    success = assign_user_role(db, user_id, role_assignment.role_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al asignar rol al usuario"
        )
    
    return {"message": "Rol asignado correctamente"}


def check_permission_logic(
    db: Session, 
    user_id: uuid.UUID, 
    module_name: str, 
    permission_type: str
) -> PermissionCheck:
    """Business logic for checking user permission"""
    
    # Validate permission type
    valid_permissions = ["create", "read", "update", "delete", "approve", "export"]
    if permission_type not in valid_permissions:
        return PermissionCheck(
            has_permission=False,
            message=f"Tipo de permiso inválido. Debe ser uno de: {', '.join(valid_permissions)}"
        )
    
    # Check permission via repository
    has_permission = check_user_permission(db, user_id, module_name, permission_type)
    
    message = "Permiso concedido" if has_permission else "Permiso denegado"
    
    return PermissionCheck(
        has_permission=has_permission,
        message=message
    )