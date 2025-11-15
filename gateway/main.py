"""
API Gateway - Sistema de Gestión de Archivos y Mensajes
Orquesta múltiples microservicios del sistema
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import httpx
from typing import Optional, List
import os
from datetime import datetime

# Configuración de URLs de microservicios
FILE_SERVICE_URL = os.getenv("FILE_SERVICE_URL", "http://134.199.176.197")
MESSAGE_SERVICE_URL = os.getenv("MESSAGE_SERVICE_URL", "http://localhost:8081")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8082")
THREAD_SERVICE_URL = os.getenv("THREAD_SERVICE_URL", "http://localhost:8083")

app = FastAPI(
    title="API Gateway - Sistema de Archivos",
    description="Gateway centralizado para todos los microservicios del sistema",
    version="1.0.0"
)

# CORS para permitir acceso desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cliente HTTP para llamadas a microservicios
http_client = httpx.AsyncClient(timeout=30.0)


# ==================== HEALTH CHECK ====================
@app.get("/health")
async def health_check():
    """Health check del gateway"""
    return {
        "status": "ok",
        "service": "api-gateway",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health/services")
async def check_services():
    """Verifica el estado de todos los microservicios"""
    services_status = {}
    
    # Verificar servicio de archivos
    try:
        response = await http_client.get(f"{FILE_SERVICE_URL}/healthz", timeout=5.0)
        services_status["files"] = {
            "status": "up" if response.status_code == 200 else "down",
            "url": FILE_SERVICE_URL
        }
    except Exception as e:
        services_status["files"] = {"status": "down", "error": str(e)}
    
    # Verificar otros servicios (ejemplo)
    # TODO: Añadir verificación de otros microservicios
    
    return {
        "gateway": "up",
        "services": services_status
    }


# ==================== SERVICIO DE ARCHIVOS ====================
@app.post("/api/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    message_id: Optional[str] = Form(None),
    thread_id: Optional[str] = Form(None)
):
    """
    Sube un archivo al servicio de archivos
    
    - **file**: Archivo a subir
    - **message_id**: ID del mensaje asociado (opcional)
    - **thread_id**: ID del hilo asociado (opcional)
    """
    try:
        # Preparar el archivo para reenvío
        files = {"file": (file.filename, await file.read(), file.content_type)}
        data = {}
        if message_id:
            data["message_id"] = message_id
        if thread_id:
            data["thread_id"] = thread_id
        
        # Llamar al microservicio de archivos
        response = await http_client.post(
            f"{FILE_SERVICE_URL}/v1/files",
            files=files,
            data=data
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json()
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Error comunicando con servicio de archivos: {str(e)}"
        )


@app.get("/api/files/{file_id}")
async def get_file(file_id: str):
    """Obtiene información de un archivo"""
    try:
        response = await http_client.get(f"{FILE_SERVICE_URL}/v1/files/{file_id}")
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json()
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Error comunicando con servicio de archivos: {str(e)}"
        )


@app.get("/api/files")
async def list_files(
    message_id: Optional[str] = None,
    thread_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """Lista archivos filtrados por mensaje o hilo"""
    try:
        params = {"limit": limit, "offset": offset}
        if message_id:
            params["message_id"] = message_id
        if thread_id:
            params["thread_id"] = thread_id
        
        response = await http_client.get(
            f"{FILE_SERVICE_URL}/v1/files",
            params=params
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json()
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Error comunicando con servicio de archivos: {str(e)}"
        )


@app.delete("/api/files/{file_id}")
async def delete_file(file_id: str):
    """Elimina un archivo (soft delete)"""
    try:
        response = await http_client.delete(f"{FILE_SERVICE_URL}/v1/files/{file_id}")
        
        if response.status_code == 204:
            return {"message": "Archivo eliminado exitosamente"}
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json()
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Error comunicando con servicio de archivos: {str(e)}"
        )


@app.post("/api/files/{file_id}/download-url")
async def get_download_url(file_id: str):
    """Obtiene URL de descarga pre-firmada"""
    try:
        response = await http_client.post(
            f"{FILE_SERVICE_URL}/v1/files/{file_id}/presign-download"
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json()
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Error comunicando con servicio de archivos: {str(e)}"
        )


# ==================== SERVICIO DE MENSAJES ====================
# TODO: Integrar con el microservicio de mensajes de otro equipo
@app.post("/api/messages")
async def create_message(message_data: dict):
    """Crea un nuevo mensaje (placeholder)"""
    # TODO: Implementar llamada al servicio de mensajes
    return {
        "message": "Endpoint pendiente de integración con servicio de mensajes",
        "data": message_data
    }


@app.get("/api/messages/{message_id}")
async def get_message(message_id: str):
    """Obtiene un mensaje por ID (placeholder)"""
    # TODO: Implementar llamada al servicio de mensajes
    return {
        "message": "Endpoint pendiente de integración con servicio de mensajes",
        "message_id": message_id
    }


# ==================== SERVICIO DE HILOS/THREADS ====================
# TODO: Integrar con el microservicio de hilos
@app.get("/api/threads/{thread_id}")
async def get_thread(thread_id: str):
    """Obtiene un hilo por ID (placeholder)"""
    # TODO: Implementar llamada al servicio de hilos
    return {
        "message": "Endpoint pendiente de integración con servicio de hilos",
        "thread_id": thread_id
    }


@app.get("/api/threads/{thread_id}/messages")
async def get_thread_messages(thread_id: str):
    """Lista mensajes de un hilo (placeholder)"""
    # TODO: Implementar llamada al servicio de mensajes
    return {
        "message": "Endpoint pendiente de integración",
        "thread_id": thread_id,
        "messages": []
    }


# ==================== SERVICIO DE USUARIOS ====================
# TODO: Integrar con el microservicio de usuarios
@app.get("/api/users/{user_id}")
async def get_user(user_id: str):
    """Obtiene información de un usuario (placeholder)"""
    # TODO: Implementar llamada al servicio de usuarios
    return {
        "message": "Endpoint pendiente de integración con servicio de usuarios",
        "user_id": user_id
    }


# ==================== ENDPOINTS COMPUESTOS ====================
@app.get("/api/messages/{message_id}/with-files")
async def get_message_with_files(message_id: str):
    """
    Obtiene un mensaje con todos sus archivos asociados
    Ejemplo de endpoint que combina múltiples microservicios
    """
    try:
        # TODO: Obtener mensaje del servicio de mensajes
        # message = await http_client.get(f"{MESSAGE_SERVICE_URL}/messages/{message_id}")
        
        # Obtener archivos del servicio de archivos
        files_response = await http_client.get(
            f"{FILE_SERVICE_URL}/v1/files",
            params={"message_id": message_id}
        )
        
        files = files_response.json() if files_response.status_code == 200 else []
        
        return {
            "message_id": message_id,
            "message": "Pendiente integración con servicio de mensajes",
            "files": files
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo mensaje con archivos: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
