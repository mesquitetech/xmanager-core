"""
Sistema automático de notificaciones de pagos pendientes y vencidos.
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, text
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from db.database import SessionLocal
from models import Site, SiteLegalInfo, Notification, NotificationTypeEnum
from api.notifications.services import NotificationService


class PaymentNotificationsManager:
    """
    Gestiona las notificaciones automáticas de pagos pendientes y vencidos.
    """
    
    @staticmethod
    def check_and_create_payment_notifications():
        """
        Revisa todos los sitios y crea notificaciones para pagos pendientes y vencidos.
        """
        db = SessionLocal()
        try:
            print("🔍 Iniciando revisión de notificaciones de pagos...")
            
            # Revisar pagos pendientes (próximos a vencer)
            pending_count = PaymentNotificationsManager._check_pending_payments(db)
            
            # Revisar pagos vencidos
            overdue_count = PaymentNotificationsManager._check_overdue_payments(db)
            
            print(f"✅ Revisión completada: {pending_count} notificaciones de pendientes, {overdue_count} notificaciones de vencidos")
            
            return {"pending": pending_count, "overdue": overdue_count}
            
        except Exception as e:
            print(f"❌ Error en revisión de notificaciones: {e}")
            db.rollback()
            return {"error": str(e)}
        finally:
            db.close()
    
    @staticmethod
    def _check_pending_payments(db: Session):
        """
        Revisa pagos que vencen en los próximos 7 días y crea notificaciones.
        """
        print("📅 Revisando pagos pendientes...")
        
        current_date = datetime.now(timezone.utc)
        upcoming_due_date = current_date + timedelta(days=7)
        
        # Buscar sitios con pagos que vencen pronto
        sites_with_upcoming_payments = db.query(Site, SiteLegalInfo).join(
            SiteLegalInfo, Site.id == SiteLegalInfo.site_id
        ).filter(
            and_(
                SiteLegalInfo.next_payment_date.isnot(None),
                SiteLegalInfo.next_payment_date >= current_date,
                SiteLegalInfo.next_payment_date <= upcoming_due_date,
                SiteLegalInfo.payment_status != "paid"
            )
        ).all()
        
        notification_count = 0
        
        for site, legal_info in sites_with_upcoming_payments:
            # Verificar si ya existe una notificación pendiente reciente
            existing_notification = db.query(Notification).filter(
                and_(
                    Notification.notification_type == NotificationTypeEnum.PAYMENT,
                    Notification.related_id == site.id,
                    Notification.metadata.op('->>')('action') == "pending",
                    Notification.created_at > datetime.now(timezone.utc) - timedelta(days=3)
                )
            ).first()
            
            if not existing_notification:
                try:
                    NotificationService.create_payment_notification(
                        db=db,
                        action="pending",
                        site_name=site.name,
                        site_id=site.id,
                        amount=legal_info.monthly_rent,
                        due_date=legal_info.next_payment_date
                    )
                    notification_count += 1
                    print(f"📋 Notificación pendiente creada para {site.name}")
                except Exception as e:
                    print(f"❌ Error creando notificación pendiente para {site.name}: {e}")
        
        return notification_count
    
    @staticmethod
    def _check_overdue_payments(db: Session):
        """
        Revisa pagos vencidos y crea notificaciones urgentes.
        """
        print("🚨 Revisando pagos vencidos...")
        
        current_date = datetime.now(timezone.utc)
        
        # Buscar sitios con pagos vencidos
        sites_with_overdue_payments = db.query(Site, SiteLegalInfo).join(
            SiteLegalInfo, Site.id == SiteLegalInfo.site_id
        ).filter(
            and_(
                SiteLegalInfo.next_payment_date.isnot(None),
                SiteLegalInfo.next_payment_date < current_date,
                SiteLegalInfo.payment_status != "paid"
            )
        ).all()
        
        notification_count = 0
        
        for site, legal_info in sites_with_overdue_payments:
            # Verificar si ya existe una notificación de vencido reciente
            existing_notification = db.query(Notification).filter(
                and_(
                    Notification.notification_type == NotificationTypeEnum.PAYMENT,
                    Notification.related_id == site.id,
                    Notification.metadata.op('->>')('action') == "overdue",
                    Notification.created_at > datetime.now(timezone.utc) - timedelta(days=1)
                )
            ).first()
            
            if not existing_notification:
                try:
                    NotificationService.create_payment_notification(
                        db=db,
                        action="overdue",
                        site_name=site.name,
                        site_id=site.id,
                        amount=legal_info.monthly_rent,
                        due_date=legal_info.next_payment_date
                    )
                    notification_count += 1
                    print(f"🚨 Notificación vencida creada para {site.name}")
                except Exception as e:
                    print(f"❌ Error creando notificación vencida para {site.name}: {e}")
        
        return notification_count


def run_payment_notifications_check():
    """
    Función principal para ejecutar la revisión de notificaciones de pagos.
    """
    return PaymentNotificationsManager.check_and_create_payment_notifications()


if __name__ == "__main__":
    # Ejecutar revisión manual
    result = run_payment_notifications_check()
    print(f"Resultado: {result}")