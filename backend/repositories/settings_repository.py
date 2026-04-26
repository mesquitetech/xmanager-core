"""
Repository para settings - Solo interacciones con base de datos
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from models import User, UserPreference

class SettingsRepository:
    
    @staticmethod
    def get_user_preference(db: Session, user_id: str, key: str) -> Optional[UserPreference]:
        """Obtener una preferencia específica del usuario"""
        return db.query(UserPreference).filter(
            UserPreference.user_id == user_id,
            UserPreference.key == key
        ).first()
    
    @staticmethod
    def get_all_user_preferences(db: Session, user_id: str) -> List[UserPreference]:
        """Obtener todas las preferencias del usuario"""
        return db.query(UserPreference).filter(
            UserPreference.user_id == user_id
        ).all()
    
    @staticmethod
    def create_user_preference(db: Session, user_id: str, key: str, value: str) -> UserPreference:
        """Crear nueva preferencia de usuario"""
        new_preference = UserPreference(
            user_id=user_id,
            key=key,
            value=value
        )
        db.add(new_preference)
        return new_preference
    
    @staticmethod
    def update_user_preference(db: Session, preference: UserPreference, value: str) -> UserPreference:
        """Actualizar preferencia existente"""
        preference.value = value
        return preference
    
    @staticmethod
    def update_user_profile(db: Session, user: User, full_name: Optional[str] = None) -> User:
        """Actualizar perfil de usuario"""
        if full_name is not None:
            user.full_name = full_name
        return user
    
    @staticmethod
    def update_user_password(db: Session, user: User, hashed_password: str) -> User:
        """Actualizar contraseña del usuario"""
        user.hashed_password = hashed_password
        return user
    
    @staticmethod
    def commit_changes(db: Session) -> None:
        """Confirmar cambios en la base de datos"""
        db.commit()
    
    @staticmethod
    def refresh_user(db: Session, user: User) -> None:
        """Refrescar datos del usuario"""
        db.refresh(user)