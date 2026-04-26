"""
Repository layer for ACL (Access Control List) operations
Handles all database interactions for roles, modules, and permissions
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
import uuid

from models import User, Role, Module, RolePermission, UserRole


def get_user_role_and_permissions(db: Session, user_id: uuid.UUID) -> Optional[Dict[str, Any]]:
    """Get user role and associated permissions"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.role_id:
            return None
            
        # Get role with permissions and modules
        role = db.query(Role).filter(Role.id == user.role_id).first()
        
        if not role:
            return None
            
        # Get role permissions separately
        role_permissions = db.query(RolePermission).options(
            joinedload(RolePermission.module)
        ).filter(RolePermission.role_id == role.id).all()
        
        # Build permissions data
        permissions = []
        for role_permission in role_permissions:
            module = role_permission.module
            if not module or not module.is_active:
                continue
                
            permission_data = {
                "module_id": module.id,
                "module_name": module.name,
                "display_name": module.display_name,
                "icon": module.icon,
                "route": module.route,
                "sort_order": module.sort_order,
                "can_create": role_permission.can_create,
                "can_read": role_permission.can_read,
                "can_update": role_permission.can_update,
                "can_delete": role_permission.can_delete,
                "can_approve": role_permission.can_approve,
                "can_export": role_permission.can_export
            }
            permissions.append(permission_data)
        
        # Sort by sort_order
        permissions.sort(key=lambda x: x["sort_order"])
        
        return {
            "user_id": user.id,
            "role_name": role.name,
            "role_display_name": role.display_name,
            "modules": permissions
        }
        
    except Exception as e:
        print(f"Error getting user permissions: {e}")
        return None


def get_all_roles(db: Session) -> List[Dict[str, Any]]:
    """Get all active roles with user counts"""
    try:
        roles = db.query(Role).filter(Role.is_active == True).all()
        
        result = []
        for role in roles:
            user_count = db.query(User).filter(User.role_id == role.id).count()
            role_data = {
                "id": role.id,
                "name": role.name,
                "display_name": role.display_name,
                "description": role.description,
                "is_active": role.is_active,
                "user_count": user_count
            }
            result.append(role_data)
        
        return result
        
    except Exception as e:
        print(f"Error getting roles: {e}")
        return []


def get_all_modules(db: Session) -> List[Dict[str, Any]]:
    """Get all active modules"""
    try:
        modules = db.query(Module).filter(Module.is_active == True).order_by(Module.sort_order).all()
        
        result = []
        for module in modules:
            module_data = {
                "id": module.id,
                "name": module.name,
                "display_name": module.display_name,
                "description": module.description,
                "icon": module.icon,
                "route": module.route,
                "sort_order": module.sort_order,
                "is_active": module.is_active
            }
            result.append(module_data)
        
        return result
        
    except Exception as e:
        print(f"Error getting modules: {e}")
        return []


def get_role_permissions(db: Session, role_id: uuid.UUID) -> List[Dict[str, Any]]:
    """Get permissions for a specific role"""  
    try:
        role_permissions = db.query(RolePermission).options(
            joinedload(RolePermission.module)
        ).filter(RolePermission.role_id == role_id).all()
        
        result = []
        for role_permission in role_permissions:
            module = role_permission.module
            if not module.is_active:
                continue
                
            permission_data = {
                "module_id": module.id,
                "module_name": module.name.value,
                "module_display_name": module.display_name,
                "can_create": role_permission.can_create,
                "can_read": role_permission.can_read,
                "can_update": role_permission.can_update,
                "can_delete": role_permission.can_delete,
                "can_approve": role_permission.can_approve,
                "can_export": role_permission.can_export
            }
            result.append(permission_data)
        
        return result
        
    except Exception as e:
        print(f"Error getting role permissions: {e}")
        return []


def update_role_permissions(db: Session, role_id: uuid.UUID, permissions: List[Dict[str, Any]]) -> bool:
    """Update permissions for a role"""
    try:
        # Delete existing permissions for this role
        db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()
        
        # Create new permissions
        for permission in permissions:
            role_permission = RolePermission(
                role_id=role_id,
                module_id=permission["module_id"],
                can_create=permission.get("can_create", False),
                can_read=permission.get("can_read", False),
                can_update=permission.get("can_update", False),
                can_delete=permission.get("can_delete", False),
                can_approve=permission.get("can_approve", False),
                can_export=permission.get("can_export", False)
            )
            db.add(role_permission)
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"Error updating role permissions: {e}")
        return False


def assign_user_role(db: Session, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
    """Assign role to user"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
            
        # Verify role exists
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            return False
            
        user.role_id = role_id
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        print(f"Error assigning user role: {e}")
        return False


def check_user_permission(db: Session, user_id: uuid.UUID, module_name: str, permission_type: str) -> bool:
    """Check if user has specific permission on a module"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.role_id:
            return False
            
        # Get role permission for the specific module
        role_permission = db.query(RolePermission).join(Module).filter(
            and_(
                RolePermission.role_id == user.role_id,
                Module.name == module_name,
                Module.is_active == True
            )
        ).first()
        
        if not role_permission:
            return False
            
        # Check specific permission
        permission_map = {
            "create": role_permission.can_create,
            "read": role_permission.can_read,
            "update": role_permission.can_update,
            "delete": role_permission.can_delete,
            "approve": role_permission.can_approve,
            "export": role_permission.can_export
        }
        
        return permission_map.get(permission_type, False)
        
    except Exception as e:
        print(f"Error checking user permission: {e}")
        return False


def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
            
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role_id": user.role_id,
            "is_active": user.is_active
        }
        
    except Exception as e:
        print(f"Error getting user: {e}")
        return None


def get_role_by_id(db: Session, role_id: uuid.UUID) -> Optional[Dict[str, Any]]:
    """Get role by ID"""
    try:
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            return None
            
        return {
            "id": role.id,
            "name": role.name.value,
            "display_name": role.display_name,
            "description": role.description,
            "is_active": role.is_active
        }
        
    except Exception as e:
        print(f"Error getting role: {e}")
        return None