"""
Supabase Storage utility — cliente centralizado para subir, descargar y eliminar
archivos en Supabase Storage. Todos los routers deben usar este módulo.

Buckets (todos privados):
  - arquitectura : diagramas de red por sitio (inventory)
  - seguros      : pólizas y contratos de seguro
  - gastos       : evidencias de gastos operacionales
  - pagos        : evidencias de pagos de renta

Flujo de archivos:
  1. upload_file()       → sube el archivo y devuelve el PATH dentro del bucket
  2. create_signed_url() → genera una URL temporal (1h) a partir del path
  3. delete_file()       → elimina el archivo usando su path
  El path se persiste en DB; la signed URL se genera on-the-fly al servir.
"""

import os
import uuid
from typing import Optional
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

BUCKETS = {
    "arquitectura": "arquitectura",
    "seguros": "seguros",
    "gastos": "gastos",
    "pagos": "pagos",
}

# Tiempo de expiración por defecto para signed URLs (1 hora)
SIGNED_URL_TTL = 3600


def get_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set to use file storage"
        )
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def upload_file(
    bucket: str,
    file_bytes: bytes,
    filename: str,
    content_type: str,
    folder: Optional[str] = None,
) -> str:
    """
    Sube un archivo a Supabase Storage.

    Returns:
        Path del archivo dentro del bucket (ej. "site_id/uuid.pdf").
        Persiste este path en la base de datos y usa create_signed_url()
        para generar una URL accesible al momento de servir el archivo.
    """
    client = get_client()
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
    unique_name = f"{uuid.uuid4()}.{ext}"
    path = f"{folder}/{unique_name}" if folder else unique_name

    client.storage.from_(bucket).upload(
        path=path,
        file=file_bytes,
        file_options={"content-type": content_type},
    )

    return path


def create_signed_url(
    bucket: str,
    path: str,
    expires_in: int = SIGNED_URL_TTL,
) -> str:
    """
    Genera una URL firmada y temporal para acceder a un archivo privado.

    Args:
        bucket: nombre del bucket (usar constantes de BUCKETS)
        path: path devuelto por upload_file() y almacenado en DB
        expires_in: segundos de validez (default 3600 = 1 hora)

    Returns:
        URL firmada accesible sin autenticación durante `expires_in` segundos.
    """
    client = get_client()
    result = client.storage.from_(bucket).create_signed_url(path, expires_in)
    # supabase-py v2 devuelve {"signedURL": "...", "error": null}
    signed_url = result.get("signedURL") or result.get("signed_url") or result.get("url")
    if not signed_url:
        raise RuntimeError(f"No se pudo generar signed URL para {bucket}/{path}: {result}")
    return signed_url


def delete_file(bucket: str, path: str) -> None:
    """
    Elimina un archivo de Supabase Storage.

    Args:
        bucket: nombre del bucket
        path: path del archivo dentro del bucket (devuelto por upload_file)
    """
    if not path:
        return
    client = get_client()
    client.storage.from_(bucket).remove([path])


def get_public_url(bucket: str, path: str) -> str:
    """
    Devuelve la URL pública de un archivo (solo para buckets públicos).
    No usar con buckets privados — usar create_signed_url() en su lugar.
    """
    client = get_client()
    return client.storage.from_(bucket).get_public_url(path)
