# app/storage.py
from minio import Minio
from datetime import timedelta
from urllib.parse import urlsplit
from .config import settings

# Cliente interno (subidas/lecturas del servicio)
_client_internal = Minio(
    settings.minio_endpoint,
    access_key=settings.minio_access_key,
    secret_key=settings.minio_secret_key,
    secure=settings.minio_secure,
)

# Cliente público solo para FIRMAR URLs con el host que verá el navegador
_pub = urlsplit(settings.public_minio_url)
_client_public = Minio(
    _pub.netloc,  # host:puerto
    access_key=settings.minio_access_key,
    secret_key=settings.minio_secret_key,
    secure=_pub.scheme == "https",
    region="us-east-1",               # <- evita lookup de región
)

def ensure_bucket():
    if not _client_internal.bucket_exists(settings.minio_bucket):
        _client_internal.make_bucket(settings.minio_bucket)

def put_object(object_key: str, data, length: int, content_type: str):
    _client_internal.put_object(settings.minio_bucket, object_key, data, length, content_type=content_type)
    return settings.minio_bucket, object_key

def presign_get(object_key: str, expires_seconds: int = 3600, filename: str = None) -> str:
    # ¡Firmamos con el cliente público! (ya no reescribimos la URL)
    # Añadimos response_content_disposition para forzar la descarga
    response_headers = {}
    if filename:
        response_headers['response-content-disposition'] = f'attachment; filename="{filename}"'
    
    return _client_public.presigned_get_object(
        settings.minio_bucket, 
        object_key, 
        expires=timedelta(seconds=expires_seconds),
        response_headers=response_headers if response_headers else None
    )
