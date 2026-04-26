"""
Servicio para gestión automática de notificaciones de pagos.
Este módulo revisa los pagos pendientes y vencidos para generar notificaciones.
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_

from db.database import get_db
from models import Site, SiteLegalInfo, Notification
from api.notifications.services import NotificationService, NotificationTypeEnum


class PaymentNotificationScheduler:
    """
    Servicio para generar notificaciones automáticas de pagos pendientes y vencidos.
    """
    
    @staticmethod
    def check_pending_payments(db: Session):
        """
        Revisar pagos pendientes y generar notificaciones para pagos que vencen pronto.
        """
        print("🔍 Revisando pagos pendientes...")
        
        # Buscar sitios con pagos que vencen en los próximos 7 días
        upcoming_due_date = datetime.now(timezone.utc) + timedelta(days=7)
        current_date = datetime.now(timezone.utc)
        
        # Obtener sitios con información legal y fecha de próximo pago
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
            # Verificar si ya existe una notificación pendiente reciente para este sitio
            existing_notification = db.query(Notification).filter(
                and_(
                    Notification.notification_type == NotificationTypeEnum.PAYMENT,
                    Notification.related_id == site.id,
                    Notification.metadata["action"].astext == "pending",
                    Notification.created_at > datetime.now(timezone.utc) - timedelta(days=3)  # No spam
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
                    print(f"📋 Notificación de pago pendiente creada para {site.name}")
                except Exception as e:
                    print(f"❌ Error creando notificación pendiente para {site.name}: {e}")
        
        print(f"✅ Se crearon {notification_count} notificaciones de pagos pendientes")
        return notification_count
    
    @staticmethod
    def check_overdue_payments(db: Session):
        """
        Revisar pagos vencidos y generar notificaciones urgentes.
        """
        print("🚨 Revisando pagos vencidos...")
        
        current_date = datetime.now(timezone.utc)
        
        # Obtener sitios con pagos vencidos
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
            # Verificar si ya existe una notificación de vencido reciente para este sitio
            existing_notification = db.query(Notification).filter(
                and_(
                    Notification.notification_type == NotificationTypeEnum.PAYMENT,
                    Notification.related_id == site.id,
                    Notification.metadata["action"].astext == "overdue",
                    Notification.created_at > datetime.now(timezone.utc) - timedelta(days=1)  # Notificación diaria
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
                    print(f"🚨 Notificación de pago vencido creada para {site.name}")
                except Exception as e:
                    print(f"❌ Error creando notificación vencida para {site.name}: {e}")
        
        print(f"✅ Se crearon {notification_count} notificaciones de pagos vencidos")
        return notification_count
    
    @staticmethod
    def run_payment_notifications_check():
        """
        Ejecutar la revisión completa de notificaciones de pagos.
        Esta función debe ser llamada periódicamente.
        """
        print("🔄 Iniciando revisión automática de notificaciones de pagos...")
        
        # Obtener sesión de base de datos
        db = next(get_db())
        
        try:
            pending_count = PaymentNotificationScheduler.check_pending_payments(db)
            overdue_count = PaymentNotificationScheduler.check_overdue_payments(db)
            
            total_notifications = pending_count + overdue_count
            print(f"🎯 Revisión completada: {total_notifications} notificaciones creadas")
            
            return {
                "success": True,
                "pending_notifications": pending_count,
                "overdue_notifications": overdue_count,
                "total_notifications": total_notifications
            }
            
        except Exception as e:
            print(f"❌ Error en revisión de notificaciones: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            db.close()