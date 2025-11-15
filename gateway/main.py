"""
API Gateway - Punto único de entrada para todos los microservicios
Integra: Usuarios, Canales, Mensajes, Moderación, Archivos, Búsqueda
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from routers import users, channels, messages, moderation, files, search

app = FastAPI(
    title="API Gateway - Sistema de Chat Universitario",
    version="1.0.0",
    description="Gateway unificado para todos los microservicios del sistema",
    docs_url="/gateway/docs",
    openapi_url="/gateway/openapi.json"
)

# CORS - Permitir frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/gateway/health")
async def health_check():
    """Health check del gateway"""
    return {
        "status": "ok",
        "service": "api-gateway",
        "version": "1.0.0"
    }

# Error handler global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "GATEWAY_ERROR",
                "message": str(exc),
                "service": "gateway"
            }
        }
    )

# Routers para cada microservicio
app.include_router(users.router, prefix="/gateway/users", tags=["Usuarios"])
app.include_router(channels.router, prefix="/gateway/channels", tags=["Canales"])
app.include_router(messages.router, prefix="/gateway/messages", tags=["Mensajes"])
app.include_router(moderation.router, prefix="/gateway/moderation", tags=["Moderación"])
app.include_router(files.router, prefix="/gateway/files", tags=["Archivos"])
app.include_router(search.router, prefix="/gateway/search", tags=["Búsqueda"])

@app.get("/")
async def root():
    """Redirige a la documentación"""
    return {
        "message": "API Gateway - Sistema de Chat",
        "docs": "/gateway/docs",
        "health": "/gateway/health"
    }
