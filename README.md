# Servicio de Archivos (Grupo 7) - Chat Universitario

Microservicio dedicado al manejo de archivos para el sistema de chat universitario basado en microservicios.

## Funcionalidades

- ✅ Subida de archivos con validación de MIME y tamaño
- ✅ Almacenamiento en MinIO (S3-compatible) 
- ✅ Generación de URLs prefirmadas para descarga
- ✅ Metadatos en PostgreSQL con idempotencia
- ✅ Publicación de eventos para indexación
- ✅ Autenticación JWT y autorización por canal
- ✅ Políticas de seguridad y cuotas por usuario

## Estructura del Proyecto

```
app/
├── api/v1/           # Endpoints REST
├── core/             # Configuración, seguridad, eventos
├── domain/           # Modelos y políticas de negocio  
├── infra/            # Infraestructura (DB, storage, messaging)
└── services/         # Lógica de aplicación
migrations/           # Migraciones de base de datos
tests/               # Tests unitarios y e2e
docker/              # Configuración Docker
```

## Desarrollo Local

### Prerrequisitos

- Python 3.13+
- Docker y Docker Compose
- Git

### Configuración

1. **Clonar el repositorio:**
   ```bash
   git clone <repo-url>
   cd INF326-2025-02.file-service
   ```

2. **Crear entorno virtual e instalar dependencias:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac  
   source venv/bin/activate
   
   pip install -e ".[dev]"
   ```

3. **Configurar variables de entorno:**
   ```bash
   cp .env.example .env
   # Editar .env con tus configuraciones
   ```

4. **Levantar servicios de desarrollo:**
   ```bash
   docker compose -f docker/docker-compose.dev.yml up -d
   ```

5. **Ejecutar migraciones:**
   ```bash
   alembic upgrade head
   ```

6. **Iniciar el servicio:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### URLs de Desarrollo

- **API:** http://localhost:8000
- **Documentación:** http://localhost:8000/docs
- **MinIO Console:** http://localhost:9001 (admin/minio123)
- **PostgreSQL:** localhost:5432 (user: files_user, db: files_db)

## Testing

```bash
# Tests unitarios
pytest tests/unit/ -v

# Tests e2e  
pytest tests/e2e/ -v

# Todos los tests con cobertura
pytest --cov=app --cov-report=html

# Linting y formato
ruff check app/
black --check app/
mypy app/
```

## API Endpoints

### Archivos

- `POST /v1/files` - Subir archivo
- `GET /v1/files/{id}` - Obtener metadatos  
- `GET /v1/files/{id}/download` - Descargar archivo
- `DELETE /v1/files/{id}` - Eliminar archivo
- `GET /v1/files?mensaje_id=...` - Listar archivos por mensaje

### Salud

- `GET /healthz` - Estado del servicio

## Configuración

Ver `.env.example` para todas las variables de entorno disponibles.

### Variables Principales

- `FILES_MAX_BYTES`: Tamaño máximo de archivo (default: 10MB)
- `FILES_ALLOWED_MIME`: MIMEs permitidos (separados por coma)
- `DB_URL`: URL de conexión a PostgreSQL  
- `STORAGE_KIND`: Tipo de almacenamiento (`s3` o `local`)
- `S3_*`: Configuración para MinIO/S3
- `JWT_PUBLIC_KEY_PEM`: Clave pública para validar JWTs

## Eventos

El servicio publica eventos `files.added` cuando se sube un archivo exitosamente:

```json
{
  "file_id": "uuid",
  "canal_id": "uuid", 
  "hilo_id": "uuid",
  "mensaje_id": "uuid",
  "owner_user_id": "uuid",
  "filename": "documento.pdf",
  "mime": "application/pdf",
  "bytes": 1024,
  "hash_sha256": "sha256_hash",
  "created_at": "2025-01-01T00:00:00Z"
}
```

## Docker

Para producción, usar la imagen Docker:

```bash
docker build -t filesvc .
docker run -p 8000:8000 --env-file .env filesvc
```
