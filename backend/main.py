import uvicorn
import os
from fastapi import FastAPI, Request, Depends, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from sqlalchemy.orm import Session
import shutil
import base64
from typing import Optional

from config import settings
from db.database import engine, Base, get_db
from db.init_postgis import init_postgis
from models import User, Site, Incident, WorkOrder, AccessLog
from api.site.router import router as site_router
from api.site.router_simple import router as site_simple_router
from api.site.router_complete import router as site_complete_router
from api.access.router import router as access_router
from api.search.router import router as search_router
from api.maintenance.router import router as maintenance_router
from api.incidents.router import router as incidents_router
from api.payments.router import router as payments_router
from api.admin.router import router as admin_router
#from api.reports.router import router as reports_router

from api.settings.router import router as settings_router
from api.expenses.router import router as expenses_router
from api.sites_direct.router import router as sites_direct_router
from api.legal.router import router as legal_router
from api.acl.router import router as acl_router
from api.seguros.router import router as seguros_router

from api.inventory.router import router as inventory_router
from api.notifications.router import router as notifications_router
from api.carriers.router import router as carriers_router
from api.transport.router import router as transport_router
# from api.frequency.router import router as frequency_router
from auth.router import router as auth_router
from auth.utils import get_current_user

# Initialize database and PostGIS with retry logic
def init_database(max_retries=3, delay=2):
    for attempt in range(max_retries):
        try:
            init_postgis()
            Base.metadata.create_all(bind=engine)
            print("Database initialized successfully")
            return
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Database initialization attempt {attempt + 1} failed, retrying in {delay} seconds...")
                import time
                time.sleep(delay)
            else:
                print(f"Database initialization failed after {max_retries} attempts")
                raise e

# Solo inicializar en desarrollo local, nunca en Vercel (serverless).
# En Vercel esta llamada falla porque Supabase usa IPv6 y el runtime es IPv4-only,
# lo que provoca FUNCTION_INVOCATION_FAILED en cada request.
if os.getenv("VERCEL") != "1":
    try:
        init_database()
    except Exception as e:
        print(f"Warning: Database initialization skipped: {e}")

app = FastAPI(
    title="XManager API",
    description="API for managing telecommunications infrastructure",
    version="1.0.0"
)

# Configure CORS — update allow_origins with the frontend URL in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
# Register more specific site routes first to avoid conflicts
app.include_router(site_complete_router, prefix="/api/sites/nuevo", tags=["Site Complete API"])
app.include_router(site_simple_router, prefix="/api/sites/simple", tags=["Site Simple API"])
# Register main site router last
app.include_router(site_router, prefix="/api/sites", tags=["Site Information"])
app.include_router(access_router, prefix="/api/access", tags=["Site Access"])
app.include_router(search_router, prefix="/api/search", tags=["Site Search"])
app.include_router(maintenance_router, prefix="/api/maintenance", tags=["Maintenance"])
app.include_router(incidents_router, prefix="/api/incidents", tags=["Incidents"])
app.include_router(payments_router, tags=["Payments"])
app.include_router(admin_router, prefix="/api/admin", tags=["Administration"])
#app.include_router(reports_router, prefix="/api/reports", tags=["Reports"])
app.include_router(settings_router, prefix="/api/settings", tags=["Settings"])
app.include_router(expenses_router, prefix="/api/expenses", tags=["Expenses"])
app.include_router(legal_router, prefix="/api/legal", tags=["Legal"])
app.include_router(inventory_router, prefix="/api/inventory", tags=["Inventory"])
app.include_router(notifications_router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(carriers_router, prefix="/api", tags=["Carriers"])
app.include_router(transport_router, prefix="/api/transport", tags=["Transport"])
# app.include_router(frequency_router, prefix="/api/frequency", tags=["Frequency Inventory"])
app.include_router(acl_router, prefix="/api/acl", tags=["Access Control"])
app.include_router(sites_direct_router)
app.include_router(seguros_router, tags=["Seguros"])


@app.get("/api/sites-direct/list")
async def get_sites_direct_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Direct sites endpoint for maps functionality"""
    try:
        sites = db.query(Site).all()
        return [
            {
                "id": str(site.id),
                "name": site.name,
                "code": site.code,
                "latitude": site.latitude,
                "longitude": site.longitude,
                "address": site.address,
                "status": site.status,
                "site_type": site.site_type
            }
            for site in sites
        ]
    except Exception as e:
        print(f"Error in sites-direct list: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error loading sites: {str(e)}"}
        )


@app.get("/api/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}


@app.get("/api/debug", tags=["Debug"])
async def debug_info():
    """Return debugging information."""
    import sys

    routes = [
        {"path": route.path, "name": route.name}
        for route in app.routes
        if hasattr(route, "path") and "/api/" in route.path
    ]

    return {
        "python_version": sys.version,
        "current_dir": os.getcwd(),
        "routes": routes,
        "api_routes": {
            "site_simple": "/api/sites/simple",
            "site": "/api/sites",
            "incidents": "/api/incidents",
            "maintenance": "/api/maintenance"
        }
    }


@app.get("/api/statistics", tags=["Statistics"])
async def get_statistics(db: Session = Depends(get_db), token: str = None):
    """Get basic system statistics."""
    try:
        total_sites = db.query(Site).count()
        total_users = db.query(User).count()
        open_incidents = db.query(Incident).filter(Incident.status != "CLOSED").count()
        pending_work_orders = db.query(WorkOrder).filter(
            WorkOrder.status.in_(["DRAFT", "IN_PROGRESS"])
        ).count()

        return {
            "total_sites": total_sites,
            "total_users": total_users,
            "open_incidents": open_incidents,
            "pending_work_orders": pending_work_orders
        }
    except Exception as e:
        return {
            "total_sites": "--",
            "total_users": "--",
            "open_incidents": "--",
            "pending_work_orders": "--",
            "error": str(e)
        }


@app.get("/api/recent-activity", tags=["Statistics"])
async def get_recent_activity(db: Session = Depends(get_db), token: str = None):
    """Get recent activity for dashboard."""
    try:
        activities = []

        recent_incidents = db.query(
            Incident,
            User.full_name.label('created_by_name'),
            Site.name.label('site_name')
        ).join(
            User, Incident.reporter_id == User.id
        ).join(
            Site, Incident.site_id == Site.id
        ).order_by(
            Incident.created_at.desc()
        ).limit(5).all()

        for incident, user_name, site_name in recent_incidents:
            action = "Reportó incidente"
            if incident.status in ("RESOLVED", "CLOSED"):
                action = "Resolvió incidente"
            activities.append({
                "date": incident.created_at,
                "user": user_name,
                "action": action,
                "details": f"{incident.title} en {site_name}"
            })

        recent_work_orders = db.query(
            WorkOrder,
            User.full_name.label('created_by_name'),
            Site.name.label('site_name')
        ).join(
            User, WorkOrder.created_by_id == User.id
        ).join(
            Site, WorkOrder.site_id == Site.id
        ).order_by(
            WorkOrder.created_at.desc()
        ).limit(5).all()

        for work_order, user_name, site_name in recent_work_orders:
            action = "Creó orden de trabajo"
            if work_order.status == "COMPLETED":
                action = "Completó mantenimiento"
            activities.append({
                "date": work_order.created_at,
                "user": user_name,
                "action": action,
                "details": f"{work_order.title} en {site_name}"
            })

        recent_access_logs = db.query(
            AccessLog,
            User.full_name.label('user_name'),
            Site.name.label('site_name')
        ).join(
            User, AccessLog.user_id == User.id
        ).join(
            Site, AccessLog.site_id == Site.id
        ).order_by(
            AccessLog.check_in_time.desc()
        ).limit(5).all()

        for access_log, user_name, site_name in recent_access_logs:
            action = "Registró salida" if access_log.check_out_time else "Registró entrada"
            activities.append({
                "date": access_log.check_out_time if access_log.check_out_time else access_log.check_in_time,
                "user": user_name,
                "action": action,
                "details": f"En {site_name} - {access_log.purpose}"
            })

        from datetime import timezone
        temp_activities = []
        for activity in activities:
            if activity["date"].tzinfo is None:
                activity["date"] = activity["date"].replace(tzinfo=timezone.utc)
            temp_activities.append((activity["date"], activity))

        temp_activities.sort(key=lambda x: x[0], reverse=True)
        activities = [item[1] for item in temp_activities[:10]]

        for activity in activities:
            activity["date"] = activity["date"].isoformat()

        return {"activities": activities}
    except Exception as e:
        import traceback
        return {
            "activities": [],
            "error": str(e),
            "detail": traceback.format_exc()
        }


@app.post("/api/test-upload")
async def test_upload_file(file: UploadFile = File(...), site_id: str = Form(...), token: Optional[str] = None):
    """Test endpoint for file uploads using FormData."""
    try:
        temp_file = f"/tmp/{file.filename}"
        with open(temp_file, "wb") as f:
            shutil.copyfileobj(file.file, f)
        file_size = os.path.getsize(temp_file)
        os.remove(temp_file)

        return {
            "success": True,
            "message": "Archivo subido correctamente",
            "details": {
                "filename": file.filename,
                "content_type": file.content_type,
                "size_bytes": file_size,
                "site_id": site_id
            }
        }
    except Exception as e:
        import traceback
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error al procesar el archivo: {str(e)}",
                "details": traceback.format_exc()
            }
        )


@app.post("/api/test-upload-base64")
async def test_upload_base64(data: dict, token: Optional[str] = None):
    """Test endpoint for file uploads using Base64 encoding."""
    try:
        file_name = data.get("file_name")
        file_type = data.get("file_type")
        file_data = data.get("file_data")
        site_id = data.get("site_id")

        if not file_data:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "No file data provided"}
            )

        try:
            decoded_data = base64.b64decode(file_data)
            file_size = len(decoded_data)
        except Exception as e:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": f"Invalid base64 data: {str(e)}"}
            )

        return {
            "success": True,
            "message": "Datos recibidos correctamente",
            "details": {
                "filename": file_name,
                "content_type": file_type,
                "size_bytes": file_size,
                "site_id": site_id
            }
        }
    except Exception as e:
        import traceback
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error al procesar los datos: {str(e)}",
                "details": traceback.format_exc()
            }
        )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
