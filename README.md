# File Service (Microservicio)

Microservicio en FastAPI para subir, descargar y eliminar archivos, asociándolos a mensajes o hilos del chat universitario. Emite eventos (por ejemplo `archivo_agregado`, `archivo_eliminado`) para que otros servicios reaccionen (Búsqueda, Moderación, etc.).

## Requisitos

- Python 3.11+ recomendado
- Instalar dependencias:

```powershell
python -m pip install -r requirements.txt
```

## Variables de entorno

- `FILE_SERVICE_DB` (opcional): ruta a la base de datos SQLite. Default: `filemeta.db`
- `FILE_SERVICE_STORAGE` (opcional): carpeta donde se guardan los archivos. Default: `storage`
- `FILE_SERVICE_EVENT_HOOKS` (opcional): URLs separadas por comas a las que se POSTearán los eventos en formato JSON. Si no está configurado, los eventos se registran en `events.log`.

Ejemplo (PowerShell):

```powershell
# $env:FILE_SERVICE_EVENT_HOOKS = "http://localhost:9001/webhook"
uvicorn app.main:app --reload
```

## Endpoints principales

- POST /upload — Form data: `file` (file), `chat_id` (string), `message_id` (string, opcional), `thread_id` (string, opcional). Devuelve `file_id`.
- GET /files/{file_id} — Descarga el archivo.
- GET /files/{file_id}/meta — Obtiene metadata del archivo.

Por defecto la API escucha en el puerto 8000 (http://127.0.0.1:8000). Si usas Docker Compose el puerto mapeado en `compose.yml` también es 8000.

Ejemplos de solicitudes (reemplaza `<file_id>` donde corresponda):

1) Subir un archivo

curl (Linux/macOS / WSL):

```bash
curl -F "file=@/ruta/a/miarchivo.pdf" -F "chat_id=curso123" -F "message_id=msg456" http://127.0.0.1:8000/upload
```

PowerShell (Windows):

```powershell
# $body = @{ file = Get-Item 'C:\ruta\a\miarchivo.pdf'; chat_id = 'curso123'; message_id = 'msg456' }
# Invoke-WebRequest -Uri http://127.0.0.1:8000/upload -Method Post -Form $body
curl -F "file=@C:\ruta\a\miarchivo.pdf" -F "chat_id=curso123" -F "message_id=msg456" http://127.0.0.1:8000/upload
```

Respuesta esperada (JSON):

```json
{ "status": "ok", "file_id": "<uuid>", "download_url": "/files/<uuid>" }
```

2) Descargar un archivo

```powershell
Invoke-WebRequest http://127.0.0.1:8000/files/<uuid> -OutFile C:\ruta\descarga.pdf
```

3) Obtener metadata

```bash
curl http://127.0.0.1:8000/files/<uuid>/meta
```

4) Eliminar un archivo

```bash
curl -X DELETE http://127.0.0.1:8000/files/<uuid>
```

5) Documentación interactiva (OpenAPI / Swagger)

Visita: http://127.0.0.1:8000/docs

## Eventos

Los eventos son JSON con al menos un campo `type` y `file` o `file_id`. Ejemplo al subir:

```json
{ "type": "archivo_agregado", "file": { ...metadata... } }
```

Si `FILE_SERVICE_EVENT_HOOKS` está configurado, el servicio intentará POSTear el evento a cada URL. Si falla o no hay hooks, los eventos se escriben en `events.log`.

## Notas

- Los archivos se guardan por su UUID interno en la carpeta de almacenamiento para evitar colisiones. La tabla SQLite `files` almacena metadata básica.
- Este microservicio es minimal y pensado para integrarse detrás de un gateway o con autenticación/ACL añadida.

## Funciones principales (archivo `app/main.py`)

Esta sección describe las funciones y endpoints más importantes en `app/main.py`, cómo se comportan y ejemplos de uso. Útil para desarrolladores que quieran integrar indexación o moderación.

- init_storage()
	- Qué hace: crea la carpeta de almacenamiento (`FILE_SERVICE_STORAGE` o `storage`) al iniciar el servicio.
	- Cuándo se ejecuta: en el evento `startup` de FastAPI.

- init_db()
	- Qué hace: crea la base de datos SQLite y la tabla `files` si no existe (`FILE_SERVICE_DB`, por defecto `filemeta.db`).
	- Cuándo se ejecuta: en `startup`.

- save_metadata(meta: dict)
	- Qué hace: inserta una fila en la tabla `files` con la metadata del archivo (id, original_name, path, content_type, size, chat_id, message_id, thread_id, created_at).
	- Uso: llamado internamente por el endpoint `/upload` después de guardar el archivo en disco.

- get_metadata(file_id: str) -> dict | None
	- Qué hace: consulta la tabla `files` por `id` y devuelve la metadata como diccionario o `None` si no existe.
	- Uso: utilizado por los endpoints `/files/{file_id}` y `/files/{file_id}/meta`.

- delete_metadata(file_id: str)
	- Qué hace: borra la fila correspondiente al `file_id` de la tabla `files`.
	- Uso: llamado por el endpoint `/files/{file_id}` (DELETE) y por rutinas de recuperación cuando el archivo físico falta.

- dispatch_event(event: dict)
	- Qué hace: intenta enviar el `event` en formato JSON a las URLs configuradas en `FILE_SERVICE_EVENT_HOOKS` (coma-separadas). Si no hay hooks o falla la entrega, escribe una línea en `events.log` como fallback.
	- Recomendación: en producción usar una cola o añadir reintentos y firma HMAC para seguridad. Ver sección "Eventos" arriba.

Endpoints clave (comportamiento resumido):

- POST /upload
	- Recibe multipart/form-data: `file` + `chat_id` (requerido) + `message_id`, `thread_id` (opcionales).
	- Guarda el archivo en `storage/<uuid>`, persistente metadata en SQLite y encola/dispatch_event del evento `archivo_agregado`.
	- Respuesta: JSON con `file_id` y `download_url` (relativo).

- GET /files/{file_id}
	- Devuelve el archivo físico como descarga. Si falta el archivo, elimina la metadata y responde 404.

- GET /files/{file_id}/meta
	- Devuelve la metadata almacenada en la BD.

- DELETE /files/{file_id}
	- Elimina el archivo físico (si existe) y la metadata; envía evento `archivo_eliminado`.

- POST /internal-upload
	- Endpoint de utilidad que lee `app/test_upload_from_main.txt` y lo envía internamente al endpoint `/upload`. Útil para pruebas y para generar registros de logs en entornos Docker.

Ejemplo de flujo (subida -> consumidor de indexación)

1. Cliente hace POST /upload con un archivo.
2. Servicio guarda archivo, guarda metadata y emite evento `archivo_agregado` (por defecto se POSTea al `FILE_SERVICE_EVENT_HOOKS` o se escribe en `events.log`).
3. Servicio de indexación (consumer) recibe el evento, descarga el archivo desde `/files/{id}`, extrae texto/meta y actualiza su índice.

Buenas prácticas para consumidores (indexación / moderación)

- No confíes en `path` devuelto por la metadata: es una ruta local. Construye la URL de descarga usando el host base del servicio (ej. `http://file-service:8000/files/{id}`) y descarga desde allí.
- Implementa idempotencia en el consumer usando `file.id` como clave de documento.
- Verifica eventos: añade firma HMAC en el emisor y valida en el receptor (puedo agregar HMAC al envío si quieres).
- Para mayor fiabilidad, usa una cola (RabbitMQ/Kafka) o una estrategia de reintentos y DLQ en vez de webhooks simples.

## Script de prueba: `scripts/upload_example.py`

Hay un script de ejemplo para automatizar una subida y ver la respuesta en consola (útil para revisar logs dentro del contenedor).

Uso local (asegúrate de tener `httpx` instalado en tu entorno o usa el `.venv`):

```powershell
.\.venv\Scripts\python scripts\upload_example.py --file C:\ruta\a\miarchivo.pdf --chat-id curso123
```

Si estás ejecutando la API dentro de Docker Compose y quieres correr el script desde el contenedor `file-service` para que su salida aparezca en los logs del contenedor:

```powershell
# Primero copia el archivo de pruebas dentro del contenedor (o monta el repo)
# Luego ejecuta (reemplaza <container_id> por el id del servicio file-service):
# docker cp scripts/upload_example.py <container_id>:/app/scripts/upload_example.py
# docker exec -it <container_id> python /app/scripts/upload_example.py --file /app/somefile.pdf --chat-id curso123
```

