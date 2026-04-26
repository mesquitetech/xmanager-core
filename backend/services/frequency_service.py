from sqlalchemy.orm import Session
import uuid
from repositories.frequency_repository import fetch_frequencies_by_site

def get_frequencies_by_site(db: Session, site_id: uuid.UUID):
    return fetch_frequencies_by_site(db, site_id)
