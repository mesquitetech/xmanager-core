import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

from config import settings

# En Vercel (serverless) cada Lambda es efímera — no tiene sentido mantener
# un pool de conexiones persistentes. NullPool abre y cierra una conexión
# por request, lo cual es correcto para serverless y evita errores de
# "connection already closed" entre invocaciones.
# En desarrollo (servidor persistente) se usa QueuePool con pool normal.
if os.getenv("VERCEL") == "1":
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=NullPool,
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=10,
        max_overflow=20,
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
