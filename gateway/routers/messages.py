"""Router para Mensajes"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from clients.messages import messages_client

router = APIRouter()

class MessageCreate(BaseModel):
    """Schema para crear mensaje - requiere thread_id en path"""
    content: str
    message_type: Optional[str] = None  # 'text', 'audio', 'file'
    paths: Optional[List[str]] = None
    user_id: str

class MessageUpdate(BaseModel):
    content: str
    user_id: str
    paths: Optional[List[str]] = None

@router.get("/threads/{thread_id}")
async def list_messages(
    thread_id: str,
    limit: int = Query(50, ge=1, le=200),
    cursor: Optional[str] = Query(None)
):
    """Listar mensajes de un thread. Thread_id es requerido."""
    result = await messages_client.list_messages(thread_id, limit, cursor)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result

@router.get("/threads/{thread_id}/messages/{message_id}")
async def get_message(thread_id: str, message_id: str):
    """Obtener un mensaje específico de un thread"""
    result = await messages_client.get_message(thread_id, message_id)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 404), detail=result)
    return result

@router.post("/threads/{thread_id}")
async def create_message(thread_id: str, message: MessageCreate):
    """
    Crear un nuevo mensaje en un thread.
    
    - thread_id: UUID del thread (requerido en path)
    - content: Contenido del mensaje (requerido)
    - message_type: 'text', 'audio', o 'file' (opcional)
    - paths: Lista de rutas de archivos asociados (opcional)
    """
    result = await messages_client.create_message(
        thread_id=thread_id,
        content=message.content,
        message_type=message.message_type,
        paths=message.paths,
        user_id=message.user_id,
    )
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result

@router.put("/threads/{thread_id}/messages/{message_id}")
async def update_message(thread_id: str, message_id: str, message: MessageUpdate):
    """Actualizar el contenido de un mensaje"""
    result = await messages_client.update_message(
        thread_id,
        message_id,
        message.content,
        user_id=message.user_id,
    )
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result

@router.delete("/threads/{thread_id}/messages/{message_id}")
async def delete_message(thread_id: str, message_id: str, user_id: str = Query(..., description="ID del usuario que ejecuta la acción")):
    """Eliminar un mensaje de un thread"""
    result = await messages_client.delete_message(thread_id, message_id, user_id=user_id)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result
