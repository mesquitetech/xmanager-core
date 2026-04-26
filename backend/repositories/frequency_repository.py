from sqlalchemy.orm import Session
import uuid
from models.frequency import SiteFrequencyInventory

def fetch_frequencies_by_site(db: Session, site_id: uuid.UUID):
    return db.query(SiteFrequencyInventory).filter(
        SiteFrequencyInventory.site_id == site_id
    ).all()
