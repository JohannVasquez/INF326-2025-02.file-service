# API Gateway - Academic Chat Platform

API Gateway centralizado que unifica los 13 microservicios del proyecto INF326.

## Microservicios Integrados

1. **Users Service** (Grupo 1) - Registro, autenticación, perfiles
2. **Channels Service** (Grupo 2) - Gestión de canales
3. **Threads Service** (Grupo 3) - Gestión de hilos
4. **Messages Service** (Grupo 4) - CRUD de mensajes
5. **Presence Service** (Grupo 5) - Estado online/offline
6. **Moderation Service** (Grupo 6) - Moderación de contenido
7. **Files Service** (Grupo 7) - Subida/descarga de archivos
8. **Search Service** (Grupo 8) - Búsqueda de contenido
9. **Academic Chatbot** (Grupo 9) - Chatbot académico
10. **Utility Chatbot** (Grupo 10) - Chatbot de utilidades
11. **Calculator Chatbot** (Grupo 11) - Chatbot calculadora
12. **Wiki Chatbot** (Grupo 12) - Chatbot Wikipedia
13. **Programming Chatbot** (Grupo 13) - Chatbot de programación

## Estructura

```
gateway/
├── app/
│   ├── main.py              # Aplicación FastAPI principal
│   ├── config.py            # Configuración de URLs de servicios
│   ├── client.py            # Cliente HTTP para microservicios
│   └── routers/
│       ├── users.py         # Endpoints de usuarios
│       ├── channels.py      # Endpoints de canales
│       ├── threads.py       # Endpoints de hilos
│       ├── messages.py      # Endpoints de mensajes
│       ├── files.py         # Endpoints de archivos
│       ├── search.py        # Endpoints de búsqueda
│       ├── presence.py      # Endpoints de presencia
│       ├── moderation.py    # Endpoints de moderación
│       └── chatbots.py      # Endpoints de chatbots
├── static/
│   ├── index.html           # Interfaz web principal
│   ├── styles.css           # Estilos
│   └── app.js               # Lógica del frontend
├── Dockerfile
├── requirements.txt
├── run.py
└── .env.example
```

## Configuración

### Variables de Entorno

Crea un archivo `.env` basado en `.env.example`:

```bash
# URLs de los microservicios
USERS_SERVICE_URL=http://users-service:8001
CHANNELS_SERVICE_URL=http://channels-service:8002
THREADS_SERVICE_URL=http://threads-service:8003
MESSAGES_SERVICE_URL=http://messages-service:8004
PRESENCE_SERVICE_URL=http://presence-service:8005
MODERATION_SERVICE_URL=http://moderation-service:8006
FILES_SERVICE_URL=http://134.199.176.197
SEARCH_SERVICE_URL=http://search-service:8008
ACADEMIC_CHATBOT_URL=http://academic-chatbot:8009
UTILITY_CHATBOT_URL=http://utility-chatbot:8010
CALC_CHATBOT_URL=http://calc-chatbot:8011
WIKI_CHATBOT_URL=http://wiki-chatbot:8012
PROGRAMMING_CHATBOT_URL=http://programming-chatbot:8013

# Configuración del gateway
GATEWAY_PORT=8000
GATEWAY_HOST=0.0.0.0
REQUEST_TIMEOUT=30
MAX_RETRIES=3
```

## Ejecución

### Local con Python

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con las URLs correctas

# Ejecutar
python run.py
```

El gateway estará disponible en http://localhost:8000

### Con Docker

```bash
# Construir imagen
docker build -t gateway:latest .

# Ejecutar contenedor
docker run -p 8000:8000 --env-file .env gateway:latest
```

## Uso de la Interfaz Web

1. **Acceder**: Abre http://localhost:8000 en tu navegador

2. **Iniciar sesión**:
   - Haz clic en "Iniciar Sesión"
   - Si no tienes cuenta, regístrate primero

3. **Crear/Unirse a canales**:
   - Navega por los canales en el sidebar
   - Crea nuevos canales con el botón "+"

4. **Participar en hilos**:
   - Selecciona un canal
   - Crea un nuevo hilo o únete a uno existente
   - Envía mensajes en tiempo real

5. **Subir archivos**:
   - En la vista de mensajes, haz clic en el botón 📎
   - Selecciona archivos para subir

6. **Usar chatbots**:
   - En el sidebar, haz clic en el chatbot deseado
   - Interactúa mediante el chat modal

7. **Buscar contenido**:
   - Haz clic en el botón 🔍
   - Escribe tu consulta

## API Endpoints

### Usuarios
- `POST /api/users/register` - Registro
- `POST /api/users/login` - Inicio de sesión
- `GET /api/users/me` - Perfil actual
- `PUT /api/users/me` - Actualizar perfil

### Canales
- `GET /api/channels` - Listar canales
- `POST /api/channels` - Crear canal
- `GET /api/channels/{id}` - Obtener canal
- `POST /api/channels/{id}/members/{user_id}` - Añadir miembro

### Hilos
- `GET /api/threads` - Listar hilos
- `POST /api/threads` - Crear hilo
- `GET /api/threads/{id}` - Obtener hilo
- `POST /api/threads/{id}/pin` - Anclar hilo

### Mensajes
- `GET /api/messages` - Listar mensajes
- `POST /api/messages` - Crear mensaje
- `PUT /api/messages/{id}` - Actualizar mensaje
- `DELETE /api/messages/{id}` - Eliminar mensaje
- `POST /api/messages/{id}/reactions` - Añadir reacción

### Archivos
- `POST /api/files/upload` - Subir archivo
- `GET /api/files` - Listar archivos
- `GET /api/files/{id}` - Obtener archivo
- `POST /api/files/{id}/presign-download` - URL de descarga

### Búsqueda
- `GET /api/search` - Buscar (query param: `q`)
- `GET /api/search/suggest` - Sugerencias

### Presencia
- `POST /api/presence/status` - Actualizar estado
- `GET /api/presence/users/{id}` - Estado de usuario
- `GET /api/presence/channel/{id}` - Usuarios en canal

### Moderación
- `POST /api/moderation/check` - Verificar contenido
- `POST /api/moderation/report` - Reportar contenido
- `POST /api/moderation/reports/{id}/action` - Acción sobre reporte

### Chatbots
- `POST /api/chatbot/academic` - Chatbot académico
- `POST /api/chatbot/utility` - Chatbot utilidades
- `POST /api/chatbot/calc` - Calculadora
- `POST /api/chatbot/wiki` - Wikipedia
- `POST /api/chatbot/programming` - Programación

## Documentación API

Una vez ejecutado, la documentación interactiva está disponible en:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Características

### Backend
- ✅ FastAPI con async/await
- ✅ Proxy inteligente con reintentos automáticos
- ✅ Manejo de errores centralizado
- ✅ CORS configurado para desarrollo
- ✅ Validación con Pydantic
- ✅ Configuración por variables de entorno

### Frontend
- ✅ Interfaz moderna tipo Discord/Slack
- ✅ Diseño responsive
- ✅ Autenticación con JWT
- ✅ Vista de canales y hilos
- ✅ Chat en tiempo real
- ✅ Integración con 5 chatbots
- ✅ Búsqueda de contenido
- ✅ Subida de archivos

## Troubleshooting

**Error: Connection refused**
- Verifica que todos los microservicios estén ejecutándose
- Revisa las URLs en el archivo `.env`

**Error: 404 Not Found**
- Verifica que los endpoints de los microservicios coincidan
- Revisa los logs del microservicio específico

**Error: CORS**
- El gateway ya tiene CORS configurado para `http://localhost:*`
- Para producción, actualiza `allow_origins` en `main.py`
