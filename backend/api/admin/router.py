from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text
from pydantic import BaseModel

from auth.utils import get_current_user, check_role
from db.database import get_db
from models import User, Role

router = APIRouter()

class UserRoleUpdate(BaseModel):
    user_id: UUID
    role_id: UUID

class UserInfo(BaseModel):
    id: UUID
    email: str
    full_name: str
    role_id: UUID
    role_name: str
    role_display_name: str
    is_active: bool
    created_at: str

class RoleInfo(BaseModel):
    id: UUID
    name: str
    display_name: str

@router.get("/users", response_model=List[UserInfo])
async def get_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todos los usuarios del sistema (solo para administradores)
    """
    # Verificar permisos usando consulta directa a la base de datos
    admin_check = db.execute(text("""
        SELECT 1 FROM role_permissions rp
        JOIN roles r ON rp.role_id = r.id
        JOIN modules m ON rp.module_id = m.id
        WHERE r.id = :role_id AND m.name = 'users' AND rp.can_read = true
    """), {"role_id": str(current_user.role_id)}).fetchone()
    
    if not admin_check:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para acceder a esta funcionalidad"
        )
    
    # Obtener todos los usuarios sin joins problemáticos
    users = db.query(User).all()
    
    result = []
    for user in users:
        # Obtener rol directamente con SQL para evitar problemas de enum
        role_query = db.execute(text("""
            SELECT name, display_name 
            FROM roles 
            WHERE id = :role_id
        """), {"role_id": str(user.role_id)})
        role_info = role_query.fetchone()
        
        role_name = role_info[0] if role_info else "sin_rol"
        role_display_name = role_info[1] if role_info else "Sin Rol"
        
        user_info = UserInfo(
            id=user.id,
            email=user.email,
            full_name=user.full_name or "Sin nombre",
            role_id=user.role_id,
            role_name=role_name,
            role_display_name=role_display_name,
            is_active=user.is_active,
            created_at=user.created_at.isoformat() if user.created_at else ""
        )
        result.append(user_info)
    
    return result

@router.get("/roles", response_model=List[RoleInfo])
async def get_all_roles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todos los roles disponibles (solo para administradores)
    """
    # Verificar permisos usando consulta directa a la base de datos
    admin_check = db.execute(text("""
        SELECT 1 FROM role_permissions rp
        JOIN roles r ON rp.role_id = r.id
        JOIN modules m ON rp.module_id = m.id
        WHERE r.id = :role_id AND m.name = 'users' AND rp.can_read = true
    """), {"role_id": str(current_user.role_id)}).fetchone()
    
    if not admin_check:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para acceder a esta funcionalidad"
        )
    
    # Obtener todos los roles usando SQL directo
    roles_query = db.execute(text("""
        SELECT id, name, display_name 
        FROM roles 
        ORDER BY display_name
    """))
    roles_data = roles_query.fetchall()
    
    result = []
    for role_data in roles_data:
        role_info = RoleInfo(
            id=role_data[0],
            name=role_data[1], 
            display_name=role_data[2]
        )
        result.append(role_info)
    
    return result

@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: UUID,
    role_update: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar el rol de un usuario (solo para administradores)
    """
    # Verificar permisos usando consulta directa a la base de datos
    admin_check = db.execute(text("""
        SELECT 1 FROM role_permissions rp
        JOIN roles r ON rp.role_id = r.id
        JOIN modules m ON rp.module_id = m.id
        WHERE r.id = :role_id AND m.name = 'users' AND rp.can_update = true
    """), {"role_id": str(current_user.role_id)}).fetchone()
    
    if not admin_check:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para cambiar roles de usuario"
        )
    
    # Verificar que el usuario a actualizar existe
    user_to_update = db.query(User).filter(User.id == user_id).first()
    if not user_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Obtener role_id del request body
    role_id = role_update.get("role_id")
    if not role_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="role_id es requerido"
        )
    
    # Verificar que el rol existe usando SQL directo
    new_role_query = db.execute(text("""
        SELECT id, name, display_name 
        FROM roles 
        WHERE id = :role_id
    """), {"role_id": str(role_id)})
    new_role_info = new_role_query.fetchone()
    
    if not new_role_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rol no encontrado"
        )
    
    # Obtener información del rol actual del usuario
    current_role_query = db.execute(text("""
        SELECT name, display_name 
        FROM roles 
        WHERE id = :role_id
    """), {"role_id": str(user_to_update.role_id)})
    current_role_info = current_role_query.fetchone()
    
    # Prevenir que se elimine el último administrador
    if current_role_info and current_role_info[0] == "administrador":
        admin_count = db.execute(text("""
            SELECT COUNT(*) FROM users u
            JOIN roles r ON u.role_id = r.id
            WHERE r.name = 'administrador'
        """)).fetchone()[0]
        
        if admin_count <= 1 and new_role_info[1] != "administrador":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede cambiar el rol del último administrador del sistema"
            )
    
    # Actualizar el rol del usuario usando SQL directo
    old_role_name = current_role_info[1] if current_role_info else "Sin Rol"
    db.execute(text("""
        UPDATE users SET role_id = :new_role_id WHERE id = :user_id
    """), {"new_role_id": str(role_id), "user_id": str(user_id)})
    
    db.commit()
    
    # Crear notificación sobre el cambio de rol
    try:
        from ..notifications.services import NotificationService
        NotificationService.create_role_assignment_notification(
            db=db,
            user_id=user_id,
            user_name=user_to_update.full_name or "Usuario",
            old_role=old_role_name,
            new_role=new_role_info[2],  # display_name
            assigned_by_id=current_user.id
        )
    except Exception as e:
        print(f"Error al crear notificación de cambio de rol: {e}")
    
    return {
        "message": f"Rol actualizado exitosamente para {user_to_update.full_name or 'Usuario'}",
        "user_id": str(user_id),
        "new_role": new_role_info[2],  # display_name
        "old_role": old_role_name
    }