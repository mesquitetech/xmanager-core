"""
Datetime utilities for handling deprecated datetime.utcnow() 
Compatible with Python 3.12+ and FastAPI 2.7
"""

from datetime import datetime, timezone


def utc_now() -> datetime:
    """
    Modern replacement for datetime.utcnow() which is deprecated in Python 3.12+
    Returns the current UTC datetime with timezone information
    """
    return datetime.now(timezone.utc)


def utc_from_timestamp(timestamp: float) -> datetime:
    """
    Create a UTC datetime from a timestamp
    """
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def utc_from_string(date_string: str) -> datetime:
    """
    Parse a date string to UTC datetime
    Handles ISO format strings with or without timezone
    """
    if date_string.endswith('Z'):
        date_string = date_string.replace('Z', '+00:00')
    
    return datetime.fromisoformat(date_string).replace(tzinfo=timezone.utc)