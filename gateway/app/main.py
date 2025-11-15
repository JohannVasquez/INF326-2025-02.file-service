"""
API Gateway Principal
Punto de entrada único para todos los microservicios
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

# Importar routers
from .routers import (
    users,
    channels,
    threads,
    messages,
    files,
    search,
    presence,
    moderation,
    chatbots
)

# Crear aplicación
app = FastAPI(
    title="Academic Chat Platform - API Gateway",
    description="Gateway unificado para todos los microservicios del sistema",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(users.router)
app.include_router(channels.router)
app.include_router(threads.router)
app.include_router(messages.router)
app.include_router(files.router)
app.include_router(search.router)
app.include_router(presence.router)
app.include_router(moderation.router)
app.include_router(chatbots.router)

# Servir archivos estáticos (frontend)
frontend_path = Path(__file__).parent.parent / "static"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Ruta raíz - sirve la interfaz web
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Sirve la interfaz web principal"""
    frontend_file = frontend_path / "index.html"
    if frontend_file.exists():
        return HTMLResponse(content=frontend_file.read_text(), status_code=200)
    return HTMLResponse(
        content="<h1>API Gateway</h1><p>Interfaz web no disponible. Visita <a href='/api/docs'>/api/docs</a> para la documentación de la API.</p>",
        status_code=200
    )

# Health check
@app.get("/health")
async def health_check():
    """Health check del gateway"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "version": "1.0.0"
    }

# Endpoint de información
@app.get("/api/info")
async def gateway_info():
    """Información sobre microservicios disponibles"""
    return {
        "gateway": "Academic Chat Platform API Gateway",
        "services": {
            "users": "Gestión de usuarios y autenticación",
            "channels": "Canales y comunidades",
            "threads": "Hilos de conversación",
            "messages": "Mensajes y respuestas",
            "files": "Subida y gestión de archivos",
            "search": "Búsqueda en contenido",
            "presence": "Estado de usuarios (online/offline)",
            "moderation": "Moderación de contenido",
            "chatbots": {
                "academic": "Chatbot académico",
                "utility": "Recordatorios y utilidades",
                "calc": "Calculadora matemática",
                "wiki": "Consultas a Wikipedia",
                "programming": "Ayuda con programación"
            }
        },
        "documentation": "/api/docs"
    }
