"""
Modelo para gestión de enlaces de transporte de telecomunicaciones
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.sql import func
from db.database import Base


class Transport(Base):
    __tablename__ = "transport_links"
    
    id = Column(Integer, primary_key=True, index=True)
    plaza = Column(String(100), nullable=False, index=True)
    enlace = Column(String(100), nullable=False, index=True)
    carrier = Column(String(100), nullable=False, index=True)
    servicio = Column(String(100), nullable=False)
    trafico_actual = Column(String(50), nullable=True)
    contacto = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    telefono = Column(String(20), nullable=True)
    id_circuito = Column(String(100), nullable=True, index=True)
    capacidad_total = Column(String(50), nullable=True)
    tipo_enlace = Column(String(50), nullable=True)  # Fibra, Microondas, Satelital
    estado = Column(String(20), nullable=True, default="Activo")  # Activo, Inactivo, Mantenimiento
    fecha_contrato = Column(DateTime, nullable=True)
    fecha_vencimiento = Column(DateTime, nullable=True)
    costo_mensual = Column(Float, nullable=True)
    notas = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'plaza': self.plaza,
            'enlace': self.enlace,
            'carrier': self.carrier,
            'servicio': self.servicio,
            'trafico_actual': self.trafico_actual,
            'contacto': self.contacto,
            'email': self.email,
            'telefono': self.telefono,
            'id_circuito': self.id_circuito,
            'capacidad_total': self.capacidad_total,
            'tipo_enlace': self.tipo_enlace,
            'estado': self.estado,
            'fecha_contrato': self.fecha_contrato.isoformat() if self.fecha_contrato else None,
            'fecha_vencimiento': self.fecha_vencimiento.isoformat() if self.fecha_vencimiento else None,
            'costo_mensual': self.costo_mensual,
            'notas': self.notas,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }