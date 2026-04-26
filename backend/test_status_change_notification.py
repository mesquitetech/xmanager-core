#!/usr/bin/env python3
"""
Script para probar las notificaciones de cambio de estado de pago
"""

import sys
import os
sys.path.append('.')

from datetime import datetime
from sqlalchemy.orm import Session
import uuid
import base64

from db.database import SessionLocal
from models import Site, SiteLegalInfo, PaymentEvidence, User, Notification

def test_status_change_notification():
    """
    Probar las notificaciones de cambio de estado
    """
    db = SessionLocal()
    try:
        print("🔍 Iniciando prueba de notificaciones de cambio de estado...")
        
        # Buscar un sitio con información legal para prueba
        site_with_legal = db.query(Site).join(
            SiteLegalInfo, Site.id == SiteLegalInfo.site_id
        ).filter(
            SiteLegalInfo.monthly_rent.isnot(None),
            SiteLegalInfo.next_payment_date.isnot(None)
        ).first()
        
        if not site_with_legal:
            print("❌ No se encontró sitio con información legal para prueba")
            return {"error": "No site found for testing"}
        
        print(f"📍 Usando sitio: {site_with_legal.name}")
        
        # Buscar usuario financiero para la prueba
        user = db.query(User).filter(User.email == "fernanda@mesquite.mx").first()
        if not user:
            print("❌ No se encontró usuario para prueba")
            return {"error": "No user found for testing"}
        
        # 1. Crear evidencia de pago (simulando carga)
        test_evidence = PaymentEvidence(
            id=uuid.uuid4(),
            site_id=site_with_legal.id,
            file_name="test_payment_evidence.pdf",
            file_type="application/pdf",
            file_data=base64.b64encode(b"test file content").decode('utf-8'),
            uploaded_by_id=user.id,
            uploaded_at=datetime.utcnow()
        )
        
        db.add(test_evidence)
        
        # 2. Actualizar el estado a pagado
        legal_info = db.query(SiteLegalInfo).filter(
            SiteLegalInfo.site_id == site_with_legal.id
        ).first()
        
        if legal_info:
            legal_info.payment_status = "paid"
            print(f"✅ Estado cambiado a 'paid' para sitio {site_with_legal.name}")
        
        db.commit()
        
        # Contar notificaciones antes
        notifications_before = db.query(Notification).filter(
            Notification.target_role == "financiero"
        ).count()
        
        print(f"📊 Notificaciones antes: {notifications_before}")
        
        # 3. Eliminar evidencia para simular cambio de estado
        print("🗑️ Eliminando evidencia para probar cambio de estado...")
        
        # Simular la lógica del endpoint de eliminación
        previous_status = legal_info.payment_status
        
        # Eliminar evidencia
        db.delete(test_evidence)
        
        # Actualizar estado según la fecha
        current_date = datetime.utcnow()
        next_payment_date = legal_info.next_payment_date
        
        new_status = None
        if next_payment_date:
            if next_payment_date < current_date:
                legal_info.payment_status = "overdue"
                new_status = "overdue"
            else:
                legal_info.payment_status = "pending"
                new_status = "pending"
        
        # Crear notificación si el estado cambió
        if previous_status == "paid" and new_status in ["pending", "overdue"]:
            from api.notifications.services import NotificationService
            
            print(f"🔄 Estado cambió de '{previous_status}' a '{new_status}'")
            
            if new_status == "overdue":
                NotificationService.create_payment_notification(
                    db=db,
                    site_id=site_with_legal.id,
                    site_name=site_with_legal.name,
                    action="status_change_overdue",
                    amount=float(legal_info.monthly_rent) if legal_info.monthly_rent else None,
                    created_by_id=user.id,
                    due_date=legal_info.next_payment_date
                )
                print("🚨 Notificación de cambio a VENCIDO creada")
            else:  # pending
                NotificationService.create_payment_notification(
                    db=db,
                    site_id=site_with_legal.id,
                    site_name=site_with_legal.name,
                    action="status_change_pending",
                    amount=float(legal_info.monthly_rent) if legal_info.monthly_rent else None,
                    created_by_id=user.id,
                    due_date=legal_info.next_payment_date
                )
                print("📋 Notificación de cambio a PENDIENTE creada")
        
        db.commit()
        
        # Contar notificaciones después
        notifications_after = db.query(Notification).filter(
            Notification.target_role == "financiero"
        ).count()
        
        print(f"📊 Notificaciones después: {notifications_after}")
        print(f"➕ Notificaciones nuevas: {notifications_after - notifications_before}")
        
        # Mostrar la última notificación creada
        latest_notification = db.query(Notification).filter(
            Notification.target_role == "financiero"
        ).order_by(Notification.created_at.desc()).first()
        
        if latest_notification:
            print(f"📢 Última notificación:")
            print(f"   - Título: {latest_notification.title}")
            print(f"   - Mensaje: {latest_notification.message}")
            print(f"   - Prioridad: {latest_notification.priority}")
        
        return {
            "success": True,
            "site_name": site_with_legal.name,
            "status_change": f"{previous_status} -> {new_status}",
            "notifications_created": notifications_after - notifications_before,
            "total_notifications": notifications_after
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
    result = test_status_change_notification()
    print(f"\nResultado final: {result}")