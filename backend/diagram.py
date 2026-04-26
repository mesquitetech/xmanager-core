# erd.py
from eralchemy import render_er
from db.database import Base

# Importar todos los modelos para que estén registrados en Base
from models import *

# Genera el diagrama
render_er(Base, "erd_from_models.png")
render_er(Base, "erd_from_models.svg")