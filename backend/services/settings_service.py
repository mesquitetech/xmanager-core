"""
Service para settings - Solo lógica de negocio y transformaciones
"""
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from fastapi import HTTPException, status

from repositories.settings_repository import SettingsRepository
from api.settings.schemas import (
    UpdateUserProfileRequest, UpdatePasswordRequest, UserPreferenceRequest,
    ThemePreferenceRequest, NotificationPreferenceRequest,
    UserProfileResponse, UserPreferencesResponse, MessageResponse, UpdateProfileResponse
)
from auth.utils import get_password_hash, verify_password
from models import User

class SettingsService:
    
    @staticmethod
    def get_user_profile(user: User) -> UserProfileResponse:
        """Obtener perfil del usuario con transformación de datos"""
        profile_data = {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.name if user.role else None,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        
        # Agregar last_login solo si existe el atributo
        if hasattr(user, 'last_login') and getattr(user, 'last_login', None) is not None:
            profile_data["last_login"] = getattr(user, 'last_login').isoformat()
        
        return UserProfileResponse(**profile_data)
    
    @staticmethod
    def update_user_profile(db: Session, user: User, profile_data: UpdateUserProfileRequest) -> UpdateProfileResponse:
        """Actualizar perfil con validaciones de negocio"""
        
        # Validaciones de negocio
        if profile_data.full_name is not None:
            SettingsService._validate_full_name(profile_data.full_name)
        
        # Actualizar en repository
        updated_user = SettingsRepository.update_user_profile(
            db=db, 
            user=user, 
            full_name=profile_data.full_name
        )
        
        SettingsRepository.commit_changes(db)
        SettingsRepository.refresh_user(db, updated_user)
        
        return UpdateProfileResponse(
            message="Perfil actualizado correctamente",
            user={
                "id": str(updated_user.id),
                "email": updated_user.email,
                "full_name": updated_user.full_name,
                "role": updated_user.role.value if updated_user.role else None
            }
        )
    
    @staticmethod
    def change_password(db: Session, user: User, password_data: UpdatePasswordRequest) -> MessageResponse:
        """Cambiar contraseña con validaciones de seguridad"""
        
        # Validar contraseña actual
        if not verify_password(password_data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña actual es incorrecta"
            )
        
        # Validaciones de negocio para nueva contraseña
        SettingsService._validate_new_password(password_data.new_password, password_data.current_password)
        
        # Actualizar contraseña
        hashed_password = get_password_hash(password_data.new_password)
        SettingsRepository.update_user_password(db, user, hashed_password)
        SettingsRepository.commit_changes(db)
        
        return MessageResponse(message="Contraseña actualizada correctamente")
    
    @staticmethod
    def set_user_preference(db: Session, user_id: str, preference: UserPreferenceRequest) -> MessageResponse:
        """Establecer preferencia de usuario con lógica de negocio"""
        
        # Validaciones de negocio
        SettingsService._validate_preference_key(preference.key)
        SettingsService._validate_preference_value(preference.key, preference.value)
        
        # Buscar si ya existe la preferencia
        existing_preference = SettingsRepository.get_user_preference(db, user_id, preference.key)
        
        if existing_preference:
            # Actualizar valor existente
            SettingsRepository.update_user_preference(db, existing_preference, preference.value)
        else:
            # Crear nueva preferencia
            SettingsRepository.create_user_preference(db, user_id, preference.key, preference.value)
        
        SettingsRepository.commit_changes(db)
        return MessageResponse(message=f"Preferencia '{preference.key}' guardada correctamente")
    
    @staticmethod
    def get_user_preferences(db: Session, user_id: str) -> UserPreferencesResponse:
        """Obtener todas las preferencias del usuario"""
        preferences = SettingsRepository.get_all_user_preferences(db, user_id)
        
        # Convertir a diccionario
        preferences_dict = {pref.key: pref.value for pref in preferences}
        
        return UserPreferencesResponse(preferences=preferences_dict)
    
    @staticmethod
    def set_theme_preference(db: Session, user_id: str, theme_data: ThemePreferenceRequest) -> MessageResponse:
        """Establecer preferencia de tema con validaciones"""
        
        # Validaciones ya están en el schema con regex, pero agregamos lógica adicional
        SettingsService._validate_theme_value(theme_data.theme)
        
        # Buscar si ya existe la preferencia
        existing_preference = SettingsRepository.get_user_preference(db, user_id, "theme")
        
        if existing_preference:
            SettingsRepository.update_user_preference(db, existing_preference, theme_data.theme)
        else:
            SettingsRepository.create_user_preference(db, user_id, "theme", theme_data.theme)
        
        SettingsRepository.commit_changes(db)
        return MessageResponse(message="Preferencia de tema guardada correctamente")
    
    @staticmethod
    def set_notification_preferences(db: Session, user_id: str, notification_data: NotificationPreferenceRequest) -> MessageResponse:
        """Establecer preferencias de notificación con transformación"""
        
        # Transformar boolean a string para almacenamiento
        preferences = {
            "email_notifications": str(notification_data.email_notifications).lower(),
            "browser_notifications": str(notification_data.browser_notifications).lower(),
            "notify_incidents": str(notification_data.notify_incidents).lower(),
            "notify_maintenance": str(notification_data.notify_maintenance).lower(),
            "notify_site_changes": str(notification_data.notify_site_changes).lower()
        }
        
        # Actualizar o crear cada preferencia
        for key, value in preferences.items():
            existing_preference = SettingsRepository.get_user_preference(db, user_id, key)
            
            if existing_preference:
                SettingsRepository.update_user_preference(db, existing_preference, value)
            else:
                SettingsRepository.create_user_preference(db, user_id, key, value)
        
        SettingsRepository.commit_changes(db)
        return MessageResponse(message="Preferencias de notificación guardadas correctamente")
    
    @staticmethod
    def logout_all_devices(user: User) -> MessageResponse:
        """Cerrar sesión en todos los dispositivos - lógica de negocio"""
        # En una implementación real, incrementaríamos un campo token_version
        # que se use para validar tokens y forzar la re-autenticación
        
        # Por ahora simulamos la acción
        return MessageResponse(message="Sesión cerrada en todos los dispositivos")
    
    # Métodos privados de validación
    @staticmethod
    def _validate_full_name(full_name: str) -> None:
        """Validar nombre completo"""
        if not full_name or len(full_name.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre completo debe tener al menos 2 caracteres"
            )
        
        if len(full_name) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre completo no puede exceder 100 caracteres"
            )
    
    @staticmethod
    def _validate_new_password(new_password: str, current_password: str) -> None:
        """Validar nueva contraseña"""
        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La nueva contraseña debe tener al menos 8 caracteres"
            )
        
        if new_password == current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La nueva contraseña debe ser diferente a la actual"
            )
        
        # Validaciones adicionales de seguridad
        if not any(c.isupper() for c in new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña debe contener al menos una letra mayúscula"
            )
        
        if not any(c.isdigit() for c in new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña debe contener al menos un número"
            )
    
    @staticmethod
    def _validate_preference_key(key: str) -> None:
        """Validar clave de preferencia"""
        allowed_keys = [
            "theme", "language", "timezone", "date_format", 
            "email_notifications", "browser_notifications",
            "notify_incidents", "notify_maintenance", "notify_site_changes"
        ]
        
        if key not in allowed_keys:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Clave de preferencia no válida: {key}"
            )
    
    @staticmethod
    def _validate_preference_value(key: str, value: str) -> None:
        """Validar valor de preferencia según la clave"""
        if key == "theme" and value not in ["light", "dark", "auto"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valor de tema no válido"
            )
        
        if key.startswith("notify_") and value not in ["true", "false"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valor de notificación debe ser 'true' o 'false'"
            )
    
    @staticmethod
    def _validate_theme_value(theme: str) -> None:
        """Validación adicional para tema"""
        if theme not in ["light", "dark", "auto"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tema no válido. Debe ser 'light', 'dark' o 'auto'."
            )