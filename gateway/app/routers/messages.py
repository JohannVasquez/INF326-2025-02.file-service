"""
Router para Servicio de Mensajes (Grupo 4)
Publicación, edición y eliminación de mensajes en hilos
"""
from fastapi import APIRouter, UploadFile, File
from typing import List, Optional
from pydantic import BaseModel
from ..client import client
from ..config import settings


router = APIRouter(prefix="/api/messages", tags=["Mensajes"])


class MessageCreate(BaseModel):
    thread_id: str
    content: str
    parent_message_id: Optional[str] = None  # Para respuestas


class Message(BaseModel):
    id: str
    thread_id: str
    content: str
    created_by: str
    created_at: str
    edited_at: Optional[str] = None
    parent_message_id: Optional[str] = None
    reactions_count: int = 0
    has_files: bool = False


@router.post("/", response_model=Message)
async def create_message(message: MessageCreate, token: str):
    """
    Publica un nuevo mensaje en un hilo
    """
    url = f"{settings.messages_service_url}/v1/messages"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.post(url, json=message.dict(), headers=headers)


@router.get("/", response_model=List[Message])
async def list_messages(
    token: str,
    thread_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """
    Lista mensajes (opcionalmente filtrados por hilo)
    """
    url = f"{settings.messages_service_url}/v1/messages"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"skip": skip, "limit": limit}
    if thread_id:
        params["thread_id"] = thread_id
    return await client.get(url, headers=headers, params=params)


@router.get("/{message_id}", response_model=Message)
async def get_message(message_id: str, token: str):
    """
    Obtiene un mensaje específico
    """
    url = f"{settings.messages_service_url}/v1/messages/{message_id}"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.get(url, headers=headers)


@router.put("/{message_id}")
async def update_message(message_id: str, content: str, token: str):
    """
    Edita un mensaje existente
    """
    url = f"{settings.messages_service_url}/v1/messages/{message_id}"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.put(url, json={"content": content}, headers=headers)


@router.delete("/{message_id}")
async def delete_message(message_id: str, token: str):
    """
    Elimina un mensaje
    """
    url = f"{settings.messages_service_url}/v1/messages/{message_id}"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.delete(url, headers=headers)


@router.post("/{message_id}/reactions")
async def add_reaction(message_id: str, emoji: str, token: str):
    """
    Agrega una reacción a un mensaje
    """
    url = f"{settings.messages_service_url}/v1/messages/{message_id}/reactions"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.post(url, json={"emoji": emoji}, headers=headers)


@router.get("/{message_id}/reactions")
async def get_reactions(message_id: str, token: str):
    """
    Obtiene reacciones de un mensaje
    """
    url = f"{settings.messages_service_url}/v1/messages/{message_id}/reactions"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.get(url, headers=headers)
