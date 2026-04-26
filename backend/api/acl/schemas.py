from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class ModulePermission(BaseModel):
    module_id: UUID
    module_name: str
    display_name: str
    icon: Optional[str] = None
    route: Optional[str] = None
    sort_order: int
    can_create: bool
    can_read: bool
    can_update: bool
    can_delete: bool
    can_approve: bool
    can_export: bool

class UserPermissions(BaseModel):
    user_id: UUID
    role_name: str
    role_display_name: str
    modules: List[ModulePermission]

class RoleInfo(BaseModel):
    id: UUID
    name: str
    display_name: str
    description: Optional[str] = None
    is_active: bool
    user_count: int

class ModuleInfo(BaseModel):
    id: UUID
    name: str
    display_name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    route: Optional[str] = None
    sort_order: int
    is_active: bool

class RoleAssignment(BaseModel):
    role_id: UUID

class RoleModulePermission(BaseModel):
    module_id: UUID
    module_name: str
    module_display_name: str
    can_create: bool
    can_read: bool
    can_update: bool
    can_delete: bool
    can_approve: bool
    can_export: bool

class PermissionCheck(BaseModel):
    has_permission: bool
    message: str