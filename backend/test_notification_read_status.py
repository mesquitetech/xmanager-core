#!/usr/bin/env python3
"""
Script para probar el estado de lectura de notificaciones
"""

import sys
import os
sys.path.append('.')

from datetime import datetime
from sqlalchemy.orm import Session
import uuid

from db.database import SessionLocal
from models import Notification, UserNotification, User

def test_notification_read_status():
    """
    Probar el estado de lectura de notificaciones
    """
    db = SessionLocal()
    try:
        print("🔍 Probando sistema de estado de lectura de notificaciones...")
        
        # Buscar usuario financiero
        user = db.query(User).filter(User.email == "fernanda@mesquite.mx").first()
        if not user:
            print("❌ Usuario financiero no encontrado")
            return {"error": "User not found"}
        
        print(f"👤 Usuario: {user.email}")
        
        # Obtener notificaciones para financiero
        notifications = db.query(Notification).filter(
            Notification.target_role == "financiero"
        ).all()
        
        print(f"📊 Total de notificaciones para financiero: {len(notifications)}")
        
        # Verificar estado de lectura para cada notificación
        read_count = 0
        unread_count = 0
        
        for notification in notifications:
            user_notification = db.query(UserNotification).filter(
                UserNotification.notification_id == notification.id,
                UserNotification.user_id == user.id
            ).first()
            
            is_read = user_notification.is_read if user_notification else False
            read_at = user_notification.read_at if user_notification else None
            
            if is_read:
                read_count += 1
                status = f"✅ LEÍDA ({read_at.strftime('%d/%m/%Y %H:%M') if read_at else 'sin fecha'})"
            else:
                unread_count += 1
                status = "📬 NO LEÍDA"
            
            print(f"   - {notification.title}: {status}")
        
        print(f"\n📈 Resumen:")
        print(f"   - Notificaciones leídas: {read_count}")
        print(f"   - Notificaciones no leídas: {unread_count}")
        
        # Simular marcar la primera notificación no leída como leída
        if notifications:
            first_notification = notifications[0]
            user_notification = db.query(UserNotification).filter(
                UserNotification.notification_id == first_notification.id,
                UserNotification.user_id == user.id
            ).first()
            
            if not user_notification:
                print(f"\n🔄 Creando estado de lectura para: {first_notification.title}")
                user_notification = UserNotification(
                    notification_id=first_notification.id,
                    user_id=user.id,
                    is_read=True,
                    read_at=datetime.utcnow()
                )
                db.add(user_notification)
                db.commit()
                print("✅ Estado de lectura creado")
            elif not user_notification.is_read:
                print(f"\n🔄 Marcando como leída: {first_notification.title}")
                user_notification.is_read = True
                user_notification.read_at = datetime.utcnow()
                db.commit()
                print("✅ Notificación marcada como leída")
            else:
                print(f"\n📝 La notificación '{first_notification.title}' ya está marcada como leída")
        
        return {
            "success": True,
            "user_email": user.email,
            "total_notifications": len(notifications),
            "read_count": read_count,
            "unread_count": unread_count
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
        
    finally:
        db.close()

if __name__ == "__main__":
    result = test_notification_read_status()
    print(f"\nResultado final: {result}")