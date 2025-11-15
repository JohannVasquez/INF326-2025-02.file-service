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

### 🌐 Servicio en Producción

El servicio está desplegado y **accesible públicamente** en DigitalOcean Kubernetes:

**🔗 URL Base:** `http://134.199.176.197`

**📝 Endpoints Públicos:**
- **Documentación API:** http://134.199.176.197/docs
- **Health Check:** http://134.199.176.197/healthz
- **OpenAPI Schema:** http://134.199.176.197/openapi.json

### ⚙️ Características del Cluster

- ✅ **Alta disponibilidad**: 2 réplicas de la API
- ✅ **Autoscaling horizontal**: HPA configurado (2-10 pods)
- ✅ **Acceso público**: Ingress con NGINX
- ✅ **CI/CD automático**: GitHub Actions
- ✅ **Almacenamiento persistente**: PostgreSQL + MinIO con PVCs

### 📊 Estado del Cluster

Para verificar el estado actual del despliegue:

```powershell
# Configurar kubectl (requerido una vez por sesión)
$env:KUBECONFIG = "c:\ruta\a\archivo\k8s-inf326-nyc1-kubeconfig.yaml"

# Obtener IP pública del servicio
.\scripts\get-ip.ps1

# Ver estado de todos los recursos
kubectl get all -n file-service

# Ver logs de la aplicación
kubectl logs -l app=file-service-api -n file-service --tail=50
```

### 🔄 CI/CD Automático

El pipeline de GitHub Actions se ejecuta automáticamente en cada push a `main`:

1. ✅ **Tests**: Ejecuta suite de pruebas
2. ✅ **Build**: Construye imagen Docker
3. ✅ **Push**: Sube imagen a Docker Hub
4. ✅ **Deploy**: Despliega al cluster de Kubernetes
5. ✅ **Health Check**: Verifica que el servicio responda

---

## 🧪 Pruebas (FastAPI Testing)

Las pruebas automatizadas validan todos los endpoints usando FastAPI Testing con `httpx.AsyncClient` y `ASGITransport` (no se levanta un servidor real). Se aíslan las dependencias externas (DB, MinIO, RabbitMQ) para que los tests sean rápidos y deterministas.

### Cómo ejecutar

```powershell
# 1) Activar entorno virtual (Windows PowerShell)
.\n+venv\Scripts\Activate.ps1

# 2) Instalar dependencias (si es necesario)
pip install -r requirements.txt

# 3) Ejecutar la suite de pruebas
pytest
```

Ejecutar un caso o archivo específico:

```powershell
pytest tests\test_files.py::test_upload_file_success -q
pytest tests\test_health.py -q
```

Cobertura (opcional):

```powershell
pip install pytest-cov
pytest --cov=app --cov-report=term-missing
```

### Qué validan los tests

- Cliente HTTP asíncrono con `httpx.AsyncClient` + `ASGITransport` para invocar la app ASGI en memoria.
- Base de datos aislada por prueba: `SQLite` en memoria con SQLAlchemy async; se hace override de la dependencia `get_session` para usar una `AsyncSession` contra un engine `sqlite+aiosqlite` efímero.
- Infraestructura parcheada con `monkeypatch` para evitar efectos colaterales:
  - MinIO: `put_object` y `presign_get` reemplazados por funciones deterministas.
  - EventBus (RabbitMQ): `connect`/`publish` reemplazados por no-ops.
  - `ensure_bucket()` anulado en startup.

### Cobertura por endpoint

- `GET /healthz`
  - Responde 200 con `{ status: "ok", service, env }`.
  - Estructura del JSON esperada.

- `POST /v1/files`
  - Éxito: carga archivo, persiste metadatos, devuelve `FileOut`.
  - Error 400 si falta `message_id` y `thread_id` (se requiere al menos uno).

- `GET /v1/files/{id}`
  - Éxito: devuelve metadatos del archivo.
  - 404 si no existe.

- `GET /v1/files?message_id=...|thread_id=...`
  - Éxito: lista filtrada por `message_id` o `thread_id`.
  - 400 si no se envía ningún filtro.

- `DELETE /v1/files/{id}`
  - Éxito: eliminación lógica; luego `GET` del mismo id devuelve 404.
  - 404 si el id no existe.

- `POST /v1/files/{id}/presign-download`
  - Éxito: retorna URL prefirmada y `expires_in`.
  - 404 si no existe el id.

### Estructura de pruebas

- `tests/conftest.py`: Fixtures principales (cliente HTTP, DB en memoria, parches de infra).
- `tests/test_health.py`: Casos de `/healthz`.
- `tests/test_files.py`: Casos de subida, listado, obtención, eliminación y presign.

En CI/CD, la etapa de Tests ejecuta esta suite automáticamente en cada push.

