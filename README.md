# Servicio de Archivos

Microservicio REST para **subir y asociar archivos** a **mensajes** o **hilos**, almacenarlos en **MinIO (S3)**, registrar metadatos en **PostgreSQL**, y **emitir eventos** a **RabbitMQ** para indexación. Incluye versionamiento de API (`/v1`), migraciones con **Alembic**, manejo de errores consistente y documentación OpenAPI automática.

Grupo 7 – Servicio de Archivos
Felipe Campaña 202173517-8
Johann Vasquez 202173577-1
Javier Gomez 202173519-4

## LINK VIDEO

https://1drv.ms/v/c/cd32fe963975dbf4/EbImFpuroc9PkcE-dCCIo5MBRrQUZvmNzHnoPej16ALBYg

## Stack
- FastAPI + Uvicorn
- PostgreSQL 16 + SQLAlchemy 2 + Alembic
- MinIO (S3 compatible) con URLs pre-firmadas
- RabbitMQ (exchange `files`, routing key `files.added.v1`)
- Docker & docker-compose

## Endpoints (v1)
- `POST /v1/files` — Sube archivo (`multipart/form-data`) y lo asocia a `message_id` o `thread_id`. Emite `files.added.v1`.
- `GET /v1/files/{id}` — Obtiene metadatos del archivo.
- `GET /v1/files` — Lista por `message_id` o `thread_id`.
- `DELETE /v1/files/{id}` — Eliminación lógica. Emite `files.deleted.v1`.
- `POST /v1/files/{id}/presign-download` — Devuelve URL prefirmada de descarga.
- `GET /healthz` — Healthcheck.

## Rápido inicio

```bash
cp .env.example .env #en caso de que salga una advertencia hay que activar esta configuración "python.terminal.useEnvFile"
docker compose up --build
# API: http://localhost:8080/docs
# MinIO Console: http://localhost:9001 (user/pass del .env)
# RabbitMQ Mgmt: http://localhost:15672
```
Si falla por migraciones en frío, reintenta:
```bash
docker compose exec api alembic upgrade head
```

## Flujo
1. Cliente llama `POST /v1/files` con archivo + `message_id` o `thread_id`.
2. Servicio guarda objeto en MinIO (bucket `${MINIO_BUCKET}`).
3. Servicio crea registro en Postgres (metadatos, checksum).
4. Servicio emite evento en RabbitMQ:
```json
{
  "type": "files.added.v1",
  "occurred_at": "2025-10-19T23:59:59Z",
  "data": {
    "file_id": "uuid",
    "bucket": "files",
    "object_key": "uuid/filename.ext",
    "mime_type": "application/pdf",
    "size": 12345,
    "message_id": "uuid|null",
    "thread_id": "uuid|null",
    "checksum_sha256": "hex"
  }
}
```

## Migraciones
- Crear nueva migración:
```bash
docker compose exec api alembic revision -m "lo que cambió"
```
- Aplicar migraciones:
```bash
docker compose exec api alembic upgrade head
```

## Errores
Respuestas de error uniformes:
```json
{ "error": { "code": "FILE_NOT_FOUND", "message": "No existe el archivo", "details": null } }
```

## Versionamiento
- Prefijo `/v1`. Cambios incompatibles -> `/v2`.

## Licencia
MIT