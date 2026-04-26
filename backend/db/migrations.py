from database import engine, Base
from alembic import command
from alembic.config import Config
import os
import sys

# Add parent directory to path so we can import models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import *

def create_tables():
    """Create all tables in models.py."""
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

def apply_migrations():
    """Apply migrations using Alembic."""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    print("Migrations applied successfully.")

if __name__ == "__main__":
    # Create tables directly if Alembic is not set up yet
    create_tables()