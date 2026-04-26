"""
Modelo de datos para Carriers (Proveedores de telecomunicaciones y transporte)
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from db.database import Base

class Carrier(Base):
    __tablename__ = "carriers"
    
    id = Column(Integer, primary_key=True, index=True)
    plaza = Column(String(100), nullable=False, index=True)
    zona = Column(String(100), nullable=False)
    proveedor = Column(String(100), nullable=False, index=True)
    ancho_banda = Column(String(50), nullable=False)
    ip = Column(String(45), nullable=False, index=True)
    contacto = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, index=True)
    telefono = Column(String(20))
    notas = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(100))
    updated_by = Column(String(100))