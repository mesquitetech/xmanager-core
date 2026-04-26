"""
Modelo de datos para seguros
"""
from sqlalchemy import Column, String, Float, Date, DateTime, Text, Boolean, ForeignKey, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.database import Base
from datetime import datetime
import uuid

class Seguro(Base):
    __tablename__ = "seguros"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), nullable=False)
    
    # Información de la aseguradora
    aseguradora = Column(String(255), nullable=False)
    contacto_aseguradora = Column(String(255))
    
    # Información de la póliza
    numero_poliza = Column(String(100))
    tipo_seguro = Column(String(100))  # responsabilidad-civil, incendio, robo, etc.
    
    # Montos
    monto_cubierto = Column(Float, nullable=False)
    cantidad_pagar = Column(Float, nullable=False)
    
    # Fechas
    fecha_pago = Column(Date, nullable=False)
    frecuencia_pago = Column(String(50), nullable=False)  # mensual, trimestral, semestral, anual
    fecha_inicio = Column(Date)
    fecha_vencimiento = Column(Date)
    
    # Estado
    estado = Column(String(50), default='vigente')  # vigente, pendiente, vencida, cancelada
    
    # Archivos — columnas legacy (LargeBinary) conservadas para compatibilidad
    poliza_filename = Column(String(255))
    poliza_content = Column(LargeBinary, nullable=True)
    poliza_content_type = Column(String(100))
    poliza_url = Column(String(500), nullable=True)  # URL en Supabase Storage

    contrato_filename = Column(String(255))
    contrato_content = Column(LargeBinary, nullable=True)
    contrato_content_type = Column(String(100))
    contrato_url = Column(String(500), nullable=True)  # URL en Supabase Storage
    
    # Metadatos
    observaciones = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    site = relationship("Site", back_populates="seguros")