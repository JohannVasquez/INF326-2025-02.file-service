# 📁 Servicio de Archivos

> Microservicio REST para **subir y asociar archivos** a **mensajes** o **hilos**, almacenarlos en **MinIO (S3)**, registrar metadatos en **PostgreSQL**, y **emitir eventos** a **RabbitMQ** para indexación. Incluye versionamiento de API (`/v1`), migraciones con **Alembic**, manejo de errores consistente y documentación OpenAPI automática.

[![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-blue?logo=kubernetes)](./KUBERNETES.md)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?logo=docker)](./Dockerfile)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=github-actions)](./.github/workflows/ci-cd.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.5-009688?logo=fastapi)](https://fastapi.tiangolo.com/)

---

**Grupo 7 – Servicio de Archivos**  
- Felipe Campaña 202173517-8  
- Johann Vasquez 202173577-1  
- Javier Gomez 202173519-4

## 🎥 LINK VIDEO

https://1drv.ms/v/c/cd32fe963975dbf4/EbImFpuroc9PkcE-dCCIo5MBRrQUZvmNzHnoPej16ALBYg

---

## 🎯 Características Principales

✅ **Almacenamiento S3**: MinIO para archivos escalable  
✅ **Base de datos robusta**: PostgreSQL con SQLAlchemy 2  
✅ **Mensajería asíncrona**: RabbitMQ para eventos  
✅ **Despliegue en Kubernetes**: Alta disponibilidad y autoscaling  
✅ **CI/CD**: GitHub Actions automático  
✅ **Documentación**: OpenAPI/Swagger integrada  

---

## 🛠️ Stack Tecnológico

- **Backend**: FastAPI + Uvicorn
- **Base de Datos**: PostgreSQL 16 + SQLAlchemy 2 + Alembic
- **Almacenamiento**: MinIO (S3 compatible) con URLs pre-firmadas
- **Mensajería**: RabbitMQ (exchange `files`, routing key `files.added.v1`)
- **Contenedores**: Docker & docker-compose
- **Orquestación**: Kubernetes con HPA
- **CI/CD**: GitHub Actions


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

## 🚀 Despliegue en Kubernetes

Este proyecto incluye configuración completa para Kubernetes con:
- ✅ Autoscaling horizontal (HPA)
- ✅ URL pública mediante Ingress
- ✅ CI/CD con GitHub Actions
- ✅ Alta disponibilidad con múltiples réplicas

### Guía Rápida

1. **Configurar kubectl**:
```powershell
$env:KUBECONFIG="c:\Users\pipe2\OneDrive\Documentos\GitHub\INF326-2025-02.file-service\k8s-inf326-nyc1-kubeconfig.yaml"
kubectl cluster-info
```

2. **Desplegar manualmente**:
```powershell
.\scripts\deploy.ps1
```

3. **Ver estado**:
```powershell
.\scripts\status.ps1
# O usar k9s para interfaz interactiva
k9s -n file-service
```

### CI/CD Automático

El pipeline de GitHub Actions se ejecuta automáticamente en push a `main` o `kubernetes`:
1. Ejecuta tests
2. Construye y sube imagen Docker
3. Despliega al cluster Kubernetes

**Ver documentación completa**: [KUBERNETES.md](./KUBERNETES.md)

## Licencia
MIT