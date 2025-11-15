# 📁 Servicio de Archivos + 🌐 API Gateway + Frontend

> **Sistema completo de Chat Universitario** que incluye:
> - Microservicio REST de archivos con **MinIO (S3)**, **PostgreSQL** y **RabbitMQ**
> - **API Gateway** (FastAPI) que integra 13 microservicios de diferentes equipos
> - **Frontend Web** (React) simple e intuitivo para interactuar con todos los servicios

[![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-blue?logo=kubernetes)](./KUBERNETES.md)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?logo=docker)](./Dockerfile)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=github-actions)](./.github/workflows/ci-cd.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.5-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB?logo=react)](https://react.dev/)

> **📖 Ver documentación completa del Gateway + Frontend**: [GATEWAY_README.md](./GATEWAY_README.md)

---

**Grupo 7 – Servicio de Archivos**  
- Felipe Campaña 202173517-8  
- Johann Vasquez 202173577-1  
- Javier Gomez 202173519-4

## 🎯 Características Principales

### Servicio de Archivos (Original)
✅ **Almacenamiento S3**: MinIO para archivos escalable  
✅ **Base de datos robusta**: PostgreSQL con SQLAlchemy 2  
✅ **Mensajería asíncrona**: RabbitMQ para eventos  
✅ **Despliegue en Kubernetes**: Alta disponibilidad y autoscaling  
✅ **CI/CD**: GitHub Actions automático  
✅ **Documentación**: OpenAPI/Swagger integrada

### Sistema Completo (Nuevo)
🌐 **API Gateway**: Punto único de entrada para 13 microservicios  
🖥️ **Frontend React**: Interfaz web simple para canales, mensajes, archivos y búsqueda  
🔗 **Integración completa**: Conecta servicios de todos los equipos del curso  
📡 **5 servicios integrados**: Canales, Mensajes, Moderación, Archivos, Búsqueda  
🐳 **Docker Ready**: Dockerfiles para gateway y manifiestos K8s  
🎨 **UI Responsiva**: Diseño limpio y fácil de usar  

---

## 🛠️ Stack Tecnológico

### Servicio de Archivos
- **Backend**: FastAPI + Uvicorn
- **Base de Datos**: PostgreSQL 16 + SQLAlchemy 2 + Alembic
- **Almacenamiento**: MinIO (S3 compatible) con URLs pre-firmadas
- **Mensajería**: RabbitMQ (exchange `files`, routing key `files.added.v1`)
- **Contenedores**: Docker & docker-compose
- **Orquestación**: Kubernetes con HPA
- **CI/CD**: GitHub Actions

### API Gateway + Frontend
- **Gateway**: FastAPI + httpx + Pydantic Settings
- **Frontend**: React 18 + Vite + Axios
- **Proxy**: Vite dev server con proxy al gateway
- **Deployment**: Docker + Kubernetes
- **HTTP Client**: Cliente base asíncrono con manejo de errores
- **UI**: CSS vanilla, diseño responsive


## 🚀 Inicio Rápido

### Opción 1: Sistema Completo (Gateway + Frontend + Servicio de Archivos)

**Desarrollo local:**
```powershell
# Ejecutar todo el stack
.\scripts\start-local.ps1
```

Esto iniciará:
- API Gateway en http://localhost:8000 (ver docs en /gateway/docs)
- Frontend en http://localhost:3000
- Servicio de archivos ya deployado en Kubernetes

**Probar el gateway:**
```powershell
.\scripts\test-gateway.ps1
```

### Opción 2: Solo Servicio de Archivos

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

---

## 📡 API Endpoints

### API Gateway (`/gateway`)
> Ver documentación completa: [GATEWAY_README.md](./GATEWAY_README.md)

**Usuarios:**
- `GET /gateway/users` - Listar usuarios
- `POST /gateway/users` - Crear usuario (registro)
- `POST /gateway/users/auth/login` - Autenticar usuario
- `GET /gateway/users/{id}` - Obtener usuario

**Canales:**
- `GET /gateway/channels` - Listar canales
- `POST /gateway/channels` - Crear canal
- `DELETE /gateway/channels/{id}` - Eliminar canal

**Mensajes:**
- `GET /gateway/messages?channel_id={id}` - Listar mensajes por canal
- `POST /gateway/messages` - Crear mensaje
- `DELETE /gateway/messages/{id}` - Eliminar mensaje

**Archivos:**
- `GET /gateway/files` - Listar archivos
- `POST /gateway/files` - Subir archivo (multipart/form-data)
- `POST /gateway/files/{id}/download-url` - Obtener URL de descarga

**Búsqueda:**
- `GET /gateway/search?q={query}` - Búsqueda general
- `GET /gateway/search/messages?q={query}` - Buscar mensajes
- `GET /gateway/search/files?q={query}` - Buscar archivos

**Health:**
- `GET /gateway/health` - Estado del gateway

### Servicio de Archivos (`/v1/files`)
- `POST /v1/files` — Sube archivo (`multipart/form-data`) y lo asocia a `message_id` o `thread_id`. Emite `files.added.v1`.
- `GET /v1/files/{id}` — Obtiene metadatos del archivo.
- `GET /v1/files` — Lista por `message_id` o `thread_id`.
- `DELETE /v1/files/{id}` — Eliminación lógica. Emite `files.deleted.v1`.
- `POST /v1/files/{id}/presign-download` — Devuelve URL prefirmada de descarga.
- `GET /healthz` — Healthcheck.

---

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

