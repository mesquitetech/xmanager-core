import os
import psycopg2
from config import settings

def init_postgis():
    """
    Initialize the PostGIS extension in the PostgreSQL database.
    This needs to be run before creating tables that use geometry types.
    """
    conn = psycopg2.connect(settings.DATABASE_URL)
    conn.autocommit = True
    cursor = conn.cursor()
    
    try:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        print("PostGIS extension enabled successfully.")
    except Exception as e:
        print(f"Error enabling PostGIS extension: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    init_postgis()