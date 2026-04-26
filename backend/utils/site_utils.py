import random
import string


def generate_site_code():
    """Genera un código único para un sitio."""
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"SITE-{random_str}"