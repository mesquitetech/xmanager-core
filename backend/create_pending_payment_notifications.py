#!/usr/bin/env python3
"""
Script para generar notificaciones automáticas de pagos pendientes y vencidos
"""

import sys
import os
sys.path.append('.')

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, text
import uuid

from db.database import SessionLocal
from models import Site, SiteLegalInfo, Notification, NotificationTypeEnum, NotificationPriorityEnum

def create_pending_payment_notifications():
    """
    Crear notificaciones para pagos pendientes y vencidos
    """
    db = SessionLocal()
    try:
        print("🔍 Iniciando generación de notificaciones de pagos...")
        
        current_date = datetime.utcnow()
        upcoming_due_date = current_date + timedelta(days=7)  # Próximos 7 días
        
        # 1. Crear notificaciones para pagos pendientes (que vencen pronto)
        print("📅 Buscando pagos pendientes...")
        
        pending_sites = db.query(Site, SiteLegalInfo).join(
            SiteLegalInfo, Site.id == SiteLegalInfo.site_id
        ).filter(
            and_(
                SiteLegalInfo.next_payment_date.isnot(None),
                SiteLegalInfo.next_payment_date >= current_date,
                SiteLegalInfo.next_payment_date <= upcoming_due_date,
                SiteLegalInfo.payment_status != "paid"
            )
        ).all()
        
        pending_count = 0
        for site, legal_info in pending_sites:
            # Verificar si ya existe notificación reciente
            existing = db.query(Notification).filter(
                and_(
                    Notification.notification_type == NotificationTypeEnum.PAYMENT,
                    Notification.related_id == site.id,
                    Notification.created_at > current_date - timedelta(days=3)
                )
            ).first()
            
            if not existing:
                # Crear notificación pendiente
                notification = Notification(
                    id=uuid.uuid4(),
                    title="Pago Pendiente",
                    message=f"Pago pendiente para el sitio: {site.name}. Vence el {legal_info.next_payment_date.strftime('%d/%m/%Y')}",
                    notification_type=NotificationTypeEnum.PAYMENT,
                    target_role="financiero",
                    priority=NotificationPriorityEnum.NORMAL,
                    related_id=site.id,
                    related_table="sites",
                    metadata={
                        "action": "pending",
                        "site_name": site.name,
                        "amount": float(legal_info.monthly_rent) if legal_info.monthly_rent else None,
                        "due_date": legal_info.next_payment_date.isoformat()
                    },
                    created_at=current_date,
                    is_system_generated=True
                )
                
                db.add(notification)
                pending_count += 1
                print(f"📋 Notificación pendiente creada para {site.name}")
        
        # 2. Crear notificaciones para pagos vencidos
        print("🚨 Buscando pagos vencidos...")
        
        overdue_sites = db.query(Site, SiteLegalInfo).join(
            SiteLegalInfo, Site.id == SiteLegalInfo.site_id
        ).filter(
            and_(
                SiteLegalInfo.next_payment_date.isnot(None),
                SiteLegalInfo.next_payment_date < current_date,
                SiteLegalInfo.payment_status != "paid"
            )
        ).all()
        
        overdue_count = 0
        for site, legal_info in overdue_sites:
            # Verificar si ya existe notificación reciente
            existing = db.query(Notification).filter(
                and_(
                    Notification.notification_type == NotificationTypeEnum.PAYMENT,
                    Notification.related_id == site.id,
                    Notification.priority == NotificationPriorityEnum.URGENT,
                    Notification.created_at > current_date - timedelta(days=1)
                )
            ).first()
            
            if not existing:
                # Crear notificación vencida
                notification = Notification(
                    id=uuid.uuid4(),
                    title="Pago Vencido",
                    message=f"PAGO VENCIDO para el sitio: {site.name}. Venció el {legal_info.next_payment_date.strftime('%d/%m/%Y')}",
                    notification_type=NotificationTypeEnum.PAYMENT,
                    target_role="financiero",
                    priority=NotificationPriorityEnum.URGENT,
                    related_id=site.id,
                    related_table="sites",
                    metadata={
                        "action": "overdue",
                        "site_name": site.name,
                        "amount": float(legal_info.monthly_rent) if legal_info.monthly_rent else None,
                        "due_date": legal_info.next_payment_date.isoformat()
                    },
                    created_at=current_date,
                    is_system_generated=True
                )
                
                db.add(notification)
                overdue_count += 1
                print(f"🚨 Notificación vencida creada para {site.name}")
        
        # Confirmar cambios
        db.commit()
        
        print(f"✅ Proceso completado:")
        print(f"   - {pending_count} notificaciones de pagos pendientes")
        print(f"   - {overdue_count} notificaciones de pagos vencidos")
        
        # Verificar total de notificaciones para financiero
        total_notifications = db.query(Notification).filter(
            Notification.target_role == "financiero"
        ).count()
        
        print(f"   - {total_notifications} notificaciones totales para rol financiero")
        
        return {
            "success": True,
            "pending": pending_count,
            "overdue": overdue_count,
            "total": total_notifications
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
    result = create_pending_payment_notifications()
    print(f"\nResultado final: {result}")