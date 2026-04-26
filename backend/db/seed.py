"""
Script para sembrar datos de prueba en la base de datos.
Incluye la creación de usuarios, sitios, incidentes, órdenes de trabajo,
registros de mantenimiento y logs de acceso.
"""
from sqlalchemy.orm import Session
from db.database import get_db
from models import (
    User, UserRole, Site, Incident, IncidentStatus, IncidentPriority, 
    WorkOrder, WorkOrderStatus, MaintenanceRecord, AccessLog, Equipment,
    SiteLegalInfo, SiteNetworkInfo, SiteEnergyInfo, SiteInfrastructureInfo
)
from auth.utils import get_password_hash
from geoalchemy2.elements import WKTElement
from datetime import datetime, timedelta
import uuid
import logging
import random
import json

def create_test_users(db: Session):
    """Crear usuarios de prueba para el sistema."""
    # Verificar si ya existen usuarios de prueba
    admin_user = db.query(User).filter(User.email == "admin@test.com").first()
    
    if not admin_user:
        logging.info("Creando usuarios de prueba...")
        
        # Definir usuarios de prueba
        test_users = [
            {
                "email": "admin@test.com",
                "password": "admin123",
                "full_name": "Administrador de Prueba",
                "role": UserRole.ADMINISTRADOR
            },
            {
                "email": "noc@test.com",
                "password": "noc123",
                "full_name": "Usuario NOC",
                "role": UserRole.OPERATIVO
            },
            {
                "email": "infra@test.com",
                "password": "infra123",
                "full_name": "Usuario Infraestructura",
                "role": UserRole.OPERATIVO
            },
            {
                "email": "legal@test.com",
                "password": "legal123",
                "full_name": "Usuario Legal",
                "role": UserRole.JURIDICO
            },
            {
                "email": "comercial@test.com",
                "password": "comercial123",
                "full_name": "Usuario Comercial",
                "role": UserRole.FINANCIERO
            }
        ]
        
        # Crear usuarios
        for user_data in test_users:
            hashed_password = get_password_hash(user_data["password"])
            new_user = User(
                email=user_data["email"],
                hashed_password=hashed_password,
                full_name=user_data["full_name"],
                role=user_data["role"]
            )
            db.add(new_user)
        
        db.commit()
        logging.info("Usuarios de prueba creados exitosamente.")
    else:
        logging.info("Los usuarios de prueba ya existen.")
    
    # Devolver los usuarios para usar en otras funciones
    return db.query(User).all()

def create_test_equipment(db: Session):
    """Crear equipos de prueba para el sistema."""
    # Verificar si ya existen equipos de prueba
    equipment_count = db.query(Equipment).count()
    
    if equipment_count == 0:
        logging.info("Creando equipos de prueba...")
        
        # Definir tipos de equipos
        equipment_types = ["Router", "Switch", "Antenna", "RRU", "Generator", "AC Unit", "Battery Bank"]
        manufacturers = ["Cisco", "Huawei", "Nokia", "Ericsson", "Siemens", "ZTE", "CommScope"]
        statuses = ["Active", "Maintenance", "Repair", "Inactive", "Retired"]
        
        # Crear equipos
        for i in range(1, 21):  # Crear 20 equipos
            equipment_type = random.choice(equipment_types)
            manufacturer = random.choice(manufacturers)
            status = random.choice(statuses)
            
            purchase_date = datetime.now() - timedelta(days=random.randint(100, 1000))
            warranty_end_date = purchase_date + timedelta(days=365 * 3)  # 3 años de garantía
            
            new_equipment = Equipment(
                name=f"{manufacturer} {equipment_type} {i}",
                equipment_type=equipment_type,
                model=f"Model-{random.randint(1000, 9999)}",
                manufacturer=manufacturer,
                serial_number=f"SN-{uuid.uuid4().hex[:10].upper()}",
                purchase_date=purchase_date,
                warranty_end_date=warranty_end_date,
                status=status,
                ip_address=f"10.0.{random.randint(1, 254)}.{random.randint(1, 254)}",
                mac_address=":".join([format(random.randint(0, 255), '02x') for _ in range(6)]),
                firmware_version=f"{random.randint(1, 9)}.{random.randint(0, 9)}.{random.randint(1, 20)}",
                configuration={"setting1": "value1", "setting2": "value2"},
                location_in_site="Rack " + str(random.randint(1, 10)),
                notes="Equipo de prueba para el sistema."
            )
            db.add(new_equipment)
        
        db.commit()
        logging.info("Equipos de prueba creados exitosamente.")
    else:
        logging.info("Los equipos de prueba ya existen.")
    
    # Devolver los equipos para usar en otras funciones
    return db.query(Equipment).all()

def create_test_sites(db: Session, equipment_list):
    """Crear sitios de prueba para el sistema."""
    # Verificar si ya existen sitios de prueba
    site_count = db.query(Site).count()
    
    if site_count < 10:
        logging.info("Creando sitios de prueba...")
        
        # Definir ubicaciones de prueba (Ciudad de México y alrededores)
        locations = [
            {"name": "Site CDMX Norte", "code": "CDMX-N", "city": "Ciudad de México", "state": "CDMX", "lat": 19.4978, "lng": -99.1269},
            {"name": "Site CDMX Sur", "code": "CDMX-S", "city": "Ciudad de México", "state": "CDMX", "lat": 19.3028, "lng": -99.1526},
            {"name": "Site CDMX Este", "code": "CDMX-E", "city": "Ciudad de México", "state": "CDMX", "lat": 19.4325, "lng": -99.0733},
            {"name": "Site CDMX Oeste", "code": "CDMX-O", "city": "Ciudad de México", "state": "CDMX", "lat": 19.3956, "lng": -99.2341},
            {"name": "Site Toluca", "code": "TOL-01", "city": "Toluca", "state": "Estado de México", "lat": 19.2826, "lng": -99.6556},
            {"name": "Site Cuernavaca", "code": "CUER-01", "city": "Cuernavaca", "state": "Morelos", "lat": 18.9242, "lng": -99.2216},
            {"name": "Site Puebla", "code": "PUE-01", "city": "Puebla", "state": "Puebla", "lat": 19.0414, "lng": -98.2063},
            {"name": "Site Querétaro", "code": "QRO-01", "city": "Querétaro", "state": "Querétaro", "lat": 20.5881, "lng": -100.3899},
            {"name": "Site Pachuca", "code": "PCH-01", "city": "Pachuca", "state": "Hidalgo", "lat": 20.1011, "lng": -98.7591},
            {"name": "Site Tlaxcala", "code": "TLAX-01", "city": "Tlaxcala", "state": "Tlaxcala", "lat": 19.3139, "lng": -98.2404}
        ]
        
        # Definir tipos de sitios
        site_types = ["Rooftop", "Greenfield", "Indoor", "Shelter"]
        statuses = ["Active", "Maintenance", "Inactive", "Planning", "Construction"]
        
        # Crear sitios
        created_sites = []
        for i, location in enumerate(locations):
            # Verificar si el sitio ya existe
            existing_site = db.query(Site).filter(Site.code == location["code"]).first()
            if existing_site:
                created_sites.append(existing_site)
                continue
                
            site_type = random.choice(site_types)
            status = random.choice(statuses)
            
            # Crear punto geométrico para el sitio
            wkt_point = f"POINT({location['lng']} {location['lat']})"
            geom = WKTElement(wkt_point, srid=4326)
            
            # Crear sitio
            new_site = Site(
                name=location["name"],
                code=location["code"],
                address=f"Av. Principal #{random.randint(100, 999)}",
                city=location["city"],
                state=location["state"],
                country="México",
                zip_code=f"{random.randint(10000, 99999)}",
                latitude=location["lat"],
                longitude=location["lng"],
                geom=geom,
                site_type=site_type,
                status=status,
                description=f"Sitio de telecomunicaciones para pruebas en {location['city']}.",
                contact_name=f"Contacto {i+1}",
                contact_phone=f"+52 55 {random.randint(1000, 9999)} {random.randint(1000, 9999)}",
                contact_email=f"contacto{i+1}@ejemplo.com"
            )
            
            # Asignar equipos al sitio (entre 2 y 5 equipos por sitio)
            num_equipment = random.randint(2, 5)
            selected_equipment = random.sample(equipment_list, num_equipment)
            new_site.equipment = selected_equipment
            
            db.add(new_site)
            db.flush()  # Para obtener el ID del sitio
            
            # Crear información legal para el sitio
            legal_info = SiteLegalInfo(
                site_id=new_site.id,
                contract_start_date=datetime.now() - timedelta(days=random.randint(365, 730)),
                contract_end_date=datetime.now() + timedelta(days=random.randint(365, 1095)),
                contract_document_path="/documents/contracts/contract_" + str(i+1) + ".pdf",
                monthly_rent=random.randint(15000, 50000),
                currency="MXN",
                landlord_name=f"Propietario {i+1}",
                landlord_contact=f"+52 55 {random.randint(1000, 9999)} {random.randint(1000, 9999)}",
                landlord_email=f"propietario{i+1}@ejemplo.com",
                notes="Información legal de prueba para el sitio."
            )
            
            # Crear información de red para el sitio
            network_info = SiteNetworkInfo(
                site_id=new_site.id,
                network_topology={"type": "Star", "connections": ["Site A", "Site B"]},
                ip_ranges=f"192.168.{i+1}.0/24",
                subnet_mask="255.255.255.0",
                gateway=f"192.168.{i+1}.1",
                primary_dns="8.8.8.8",
                secondary_dns="8.8.4.4",
                bandwidth=f"{random.randint(100, 1000)} Mbps",
                isp_provider=random.choice(["Telmex", "Totalplay", "Izzi", "AT&T"]),
                network_diagram_path="/documents/network/diagram_" + str(i+1) + ".pdf",
                notes="Información de red de prueba para el sitio."
            )
            
            # Crear información de energía para el sitio
            energy_info = SiteEnergyInfo(
                site_id=new_site.id,
                power_source=random.choice(["grid", "generator", "solar", "hybrid"]),
                has_generator=random.choice([True, False]),
                generator_details={"capacity": f"{random.randint(10, 50)} kVA", "fuel_type": "Diesel"},
                has_solar=random.choice([True, False]),
                solar_details={"capacity": f"{random.randint(5, 20)} kW", "panels": random.randint(10, 40)},
                has_batteries=random.choice([True, False]),
                battery_details={"capacity": f"{random.randint(20, 100)} kWh", "type": "Lithium-Ion"},
                power_consumption=random.uniform(10.0, 50.0),
                utility_provider=random.choice(["CFE", "Iberdrola"]),
                meter_number=f"M-{random.randint(100000, 999999)}",
                electrical_diagram_path="/documents/electrical/diagram_" + str(i+1) + ".pdf",
                notes="Información de energía de prueba para el sitio."
            )
            
            # Crear información de infraestructura para el sitio
            infrastructure_info = SiteInfrastructureInfo(
                site_id=new_site.id,
                tower_type=random.choice(["monopole", "self-supporting", "guyed"]),
                tower_height=random.uniform(20.0, 60.0),
                tower_manufacturer=random.choice(["American Tower", "Torres Unidas", "Telesites"]),
                shelter_type=random.choice(["Concrete", "Prefabricated", "Container"]),
                shelter_dimensions=f"{random.randint(3, 6)}m x {random.randint(2, 4)}m",
                security_measures={"cameras": random.choice([True, False]), "access_control": random.choice([True, False]), "fence": random.choice([True, False])},
                has_air_conditioning=random.choice([True, False]),
                ac_details={"brand": random.choice(["Carrier", "LG", "Samsung"]), "capacity": f"{random.randint(12000, 24000)} BTU"},
                has_fire_protection=random.choice([True, False]),
                fire_protection_details={"type": random.choice(["Sprinkler", "FM200", "CO2"]), "sensors": random.randint(2, 8)},
                cable_routes={"main": "Route A", "backup": "Route B"},
                notes="Información de infraestructura de prueba para el sitio."
            )
            
            db.add(legal_info)
            db.add(network_info)
            db.add(energy_info)
            db.add(infrastructure_info)
            
            created_sites.append(new_site)
        
        db.commit()
        logging.info("Sitios de prueba creados exitosamente.")
    else:
        logging.info("Los sitios de prueba ya existen.")
        created_sites = db.query(Site).all()
    
    # Devolver los sitios para usar en otras funciones
    return created_sites

def create_test_incidents(db: Session, users, sites):
    """Crear incidentes de prueba para el sistema."""
    # Verificar si ya existen incidentes de prueba
    incident_count = db.query(Incident).count()
    
    if incident_count == 0:
        logging.info("Creando incidentes de prueba...")
        
        # Seleccionar usuarios por rol para reporter y assignee
        noc_users = [user for user in users if user.role == UserRole.OPERATIVO]
        infra_users = [user for user in users if user.role == UserRole.OPERATIVO]
        
        # Si no hay usuarios en esos roles, usar cualquier usuario
        reporters = noc_users if noc_users else users
        assignees = infra_users if infra_users else users
        
        # Definir categorías y títulos de incidentes
        categories = ["Electrical", "Network", "Physical", "Security", "Environmental"]
        incident_titles = [
            "Falla de energía", "Pérdida de conectividad", "Daño en torre", "Intrusión detectada", 
            "Sobrecalentamiento", "Falla de equipo", "Interferencia RF", "Daño por agua", 
            "Vandalismo", "Error de configuración"
        ]
        
        # Crear incidentes aleatorios para cada sitio
        for site in sites:
            # Número aleatorio de incidentes por sitio (0-3)
            num_incidents = random.randint(0, 3)
            
            for _ in range(num_incidents):
                reporter = random.choice(reporters)
                assignee = random.choice(assignees) if random.choice([True, False]) else None
                category = random.choice(categories)
                title = random.choice(incident_titles)
                priority = random.choice(list(IncidentPriority))
                status = random.choice(list(IncidentStatus))
                
                reported_at = datetime.now() - timedelta(days=random.randint(1, 60))
                resolved_at = None
                if status in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]:
                    resolved_at = reported_at + timedelta(hours=random.randint(1, 72))
                
                # Crear una lista de adjuntos o un diccionario para algunos incidentes
                attach = None
                if random.choice([True, False]):
                    # Crear una lista de adjuntos directamente (no como cadena JSON)
                    attach = [f"/attachments/incident_{uuid.uuid4().hex[:8]}.jpg"]
                
                incident = Incident(
                    site_id=site.id,
                    reporter_id=reporter.id,
                    assignee_id=assignee.id if assignee else None,
                    title=title,
                    description=f"Descripción del incidente: {title} en {site.name}",
                    category=category,
                    priority=priority,
                    status=status,
                    reported_at=reported_at,
                    resolved_at=resolved_at,
                    resolution_notes="Problema resuelto" if resolved_at else None,
                    attachments=attach
                )
                
                db.add(incident)
        
        db.commit()
        logging.info("Incidentes de prueba creados exitosamente.")
    else:
        logging.info("Los incidentes de prueba ya existen.")

def create_test_work_orders(db: Session, users, sites, equipment_list):
    """Crear órdenes de trabajo de prueba para el sistema."""
    # Verificar si ya existen órdenes de trabajo de prueba
    work_order_count = db.query(WorkOrder).count()
    
    if work_order_count == 0:
        logging.info("Creando órdenes de trabajo de prueba...")
        
        # Seleccionar usuarios por rol
        admin_users = [user for user in users if user.role == UserRole.ADMINISTRADOR]
        infra_users = [user for user in users if user.role == UserRole.OPERATIVO]
        
        # Si no hay usuarios en esos roles, usar cualquier usuario
        creators = admin_users if admin_users else users
        assignees = infra_users if infra_users else users
        
        # Definir tipos de trabajo y títulos
        work_types = ["Preventive", "Corrective", "Installation", "Upgrade", "Inspection"]
        work_titles = [
            "Mantenimiento preventivo", "Reparación de equipo", "Instalación de antena", 
            "Actualización de firmware", "Inspección de sitio", "Cambio de baterías", 
            "Limpieza de equipos", "Calibración de antenas"
        ]
        
        # Obtener incidentes existentes
        incidents = db.query(Incident).all()
        
        # Crear órdenes de trabajo aleatorias para cada sitio
        for site in sites:
            # Número aleatorio de órdenes por sitio (1-4)
            num_orders = random.randint(1, 4)
            
            for _ in range(num_orders):
                creator = random.choice(creators)
                assignee = random.choice(assignees) if random.choice([True, False]) else None
                work_type = random.choice(work_types)
                title = random.choice(work_titles)
                status = random.choice(list(WorkOrderStatus))
                
                # Usar un incidente relacionado en algunos casos
                site_incidents = [inc for inc in incidents if inc.site_id == site.id]
                incident_id = random.choice(site_incidents).id if site_incidents and random.choice([True, False]) else None
                
                # Fechas para la orden de trabajo
                scheduled_start = datetime.now() + timedelta(days=random.randint(-30, 30))
                scheduled_end = scheduled_start + timedelta(hours=random.randint(1, 8))
                
                actual_start = None
                actual_end = None
                if status in [WorkOrderStatus.IN_PROGRESS, WorkOrderStatus.COMPLETED]:
                    actual_start = scheduled_start + timedelta(minutes=random.randint(-60, 60))
                    if status == WorkOrderStatus.COMPLETED:
                        actual_end = actual_start + timedelta(hours=random.randint(1, 10))
                
                # Crear orden de trabajo
                work_order = WorkOrder(
                    site_id=site.id,
                    incident_id=incident_id,
                    created_by_id=creator.id,
                    assigned_to_id=assignee.id if assignee else None,
                    title=title,
                    description=f"Descripción de la orden: {title} en {site.name}",
                    work_type=work_type,
                    status=status,
                    priority=random.choice(["Low", "Medium", "High"]),
                    scheduled_start=scheduled_start,
                    scheduled_end=scheduled_end,
                    actual_start=actual_start,
                    actual_end=actual_end,
                    checklist=json.dumps({"item1": True, "item2": False, "item3": True}),
                    materials_used=["Cable RG6", "Conectores N", "Cinta aislante"] if random.choice([True, False]) else None,
                    labor_hours=random.uniform(1.0, 8.0) if actual_end else None,
                    total_cost=random.uniform(500, 5000) if status == WorkOrderStatus.COMPLETED else None,
                    attachments=[f"/attachments/workorder_{uuid.uuid4().hex[:8]}.jpg"] if random.choice([True, False]) else None,
                    notes="Notas de la orden de trabajo" if random.choice([True, False]) else None
                )
                
                db.add(work_order)
                db.flush()  # Para obtener el ID de la orden
                
                # Crear registros de mantenimiento si la orden está en progreso o completada
                if status in [WorkOrderStatus.IN_PROGRESS, WorkOrderStatus.COMPLETED]:
                    # Número aleatorio de registros (1-3)
                    num_records = random.randint(1, 3)
                    
                    for _ in range(num_records):
                        # Seleccionar equipo aleatorio del sitio
                        equipment = random.choice(site.equipment) if site.equipment else None
                        
                        maintenance_record = MaintenanceRecord(
                            work_order_id=work_order.id,
                            equipment_id=equipment.id if equipment else None,
                            maintenance_type=random.choice(["Preventive", "Corrective"]),
                            description=f"Mantenimiento de {equipment.name if equipment else 'equipo'} en {site.name}",
                            action_taken="Se realizó limpieza y verificación de funcionamiento",
                            parts_replaced=["Filtro", "Ventilador"] if random.choice([True, False]) else None,
                            performed_at=actual_start + timedelta(minutes=random.randint(30, 120)) if actual_start else datetime.now(),
                            performed_by=assignee.full_name if assignee else "Técnico",
                            next_maintenance_date=datetime.now() + timedelta(days=random.randint(30, 180)),
                            attachments=[f"/attachments/maintenance_{uuid.uuid4().hex[:8]}.jpg"] if random.choice([True, False]) else None,
                            notes="Notas del mantenimiento" if random.choice([True, False]) else None
                        )
                        
                        db.add(maintenance_record)
        
        db.commit()
        logging.info("Órdenes de trabajo y registros de mantenimiento creados exitosamente.")
    else:
        logging.info("Las órdenes de trabajo de prueba ya existen.")

def create_test_access_logs(db: Session, users, sites):
    """Crear registros de acceso de prueba para el sistema."""
    # Verificar si ya existen registros de acceso de prueba
    access_log_count = db.query(AccessLog).count()
    
    if access_log_count == 0:
        logging.info("Creando registros de acceso de prueba...")
        
        # Definir propósitos de visita
        purposes = [
            "Mantenimiento preventivo", "Reparación de equipos", "Inspección rutinaria", 
            "Actualización de sistemas", "Instalación de nuevos equipos", "Verificación de alarmas",
            "Limpieza del sitio", "Auditoría de seguridad"
        ]
        
        # Crear registros de acceso para cada sitio
        for site in sites:
            # Número aleatorio de registros por sitio (2-8)
            num_logs = random.randint(2, 8)
            
            for _ in range(num_logs):
                user = random.choice(users)
                purpose = random.choice(purposes)
                
                # Fechas de entrada y salida
                check_in_time = datetime.now() - timedelta(days=random.randint(1, 60), hours=random.randint(0, 23))
                check_out_time = check_in_time + timedelta(hours=random.randint(1, 6)) if random.random() > 0.2 else None
                
                access_log = AccessLog(
                    site_id=site.id,
                    user_id=user.id,
                    check_in_time=check_in_time,
                    check_out_time=check_out_time,
                    purpose=purpose,
                    activities=f"Se realizó {purpose.lower()} en el sitio. {random.choice(['Sin incidentes.', 'Todo en orden.', 'Se requiere seguimiento.'])}",
                    photos=[f"/photos/access_{uuid.uuid4().hex[:8]}.jpg"] if random.choice([True, False]) else None,
                    notes="Notas adicionales de la visita" if random.choice([True, False]) else None
                )
                
                db.add(access_log)
        
        db.commit()
        logging.info("Registros de acceso de prueba creados exitosamente.")
    else:
        logging.info("Los registros de acceso de prueba ya existen.")

def seed_database():
    """
    Sembrar datos de prueba en la base de datos.
    Esta función está deshabilitada para el entorno de producción.
    """
    # AMBIENTE DE PRODUCCIÓN - SEED DESHABILITADO
    logging.info("Función seed_database() deshabilitada para el entorno de producción.")
    return
    
    # Código deshabilitado para producción
    """
    # Obtener sesión de base de datos
    db = next(get_db())
    
    try:
        # Configurar nivel de logs
        logging.basicConfig(level=logging.INFO)
        
        # Crear datos de prueba en orden adecuado
        logging.info("Iniciando proceso de inicialización de datos...")
        
        # 1. Crear usuarios
        users = create_test_users(db)
        
        # 2. Crear equipos
        equipment = create_test_equipment(db)
        
        # 3. Crear sitios y relacionar con equipos
        sites = create_test_sites(db, equipment)
        
        # 4. Crear incidentes
        create_test_incidents(db, users, sites)
        
        # 5. Crear órdenes de trabajo y registros de mantenimiento
        create_test_work_orders(db, users, sites, equipment)
        
        # 6. Crear registros de acceso
        create_test_access_logs(db, users, sites)
        
        logging.info("Base de datos sembrada exitosamente.")
    except Exception as e:
        logging.error(f"Error al sembrar la base de datos: {str(e)}")
        db.rollback()
        raise
    finally:
        pass
    """
    # No cerrar db porque no se abrió
    # db.close()

# Deshabilitado para producción
if __name__ == "__main__":
    print("Seed de datos deshabilitado para el ambiente de producción.")
    # seed_database()