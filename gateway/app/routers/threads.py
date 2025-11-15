"""
Router para Servicio de Hilos (Grupo 3)
Maneja hilos dentro de cada canal
"""
from fastapi import APIRouter
from typing import List, Optional
from pydantic import BaseModel
from ..client import client
from ..config import settings


router = APIRouter(prefix="/api/threads", tags=["Hilos"])


class ThreadCreate(BaseModel):
    channel_id: str
    title: str
    content: Optional[str] = None


class Thread(BaseModel):
    id: str
    channel_id: str
    title: str
    content: Optional[str] = None
    created_by: str
    created_at: str
    messages_count: int
    is_pinned: bool = False


@router.post("/", response_model=Thread)
async def create_thread(thread: ThreadCreate, token: str):
    """
    Crea un nuevo hilo en un canal
    """
    url = f"{settings.threads_service_url}/v1/threads"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.post(url, json=thread.dict(), headers=headers)


@router.get("/", response_model=List[Thread])
async def list_threads(
    token: str,
    channel_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    """
    Lista hilos (opcionalmente filtrados por canal)
    """
    url = f"{settings.threads_service_url}/v1/threads"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"skip": skip, "limit": limit}
    if channel_id:
        params["channel_id"] = channel_id
    return await client.get(url, headers=headers, params=params)


@router.get("/{thread_id}", response_model=Thread)
async def get_thread(thread_id: str, token: str):
    """
    Obtiene detalles de un hilo
    """
    url = f"{settings.threads_service_url}/v1/threads/{thread_id}"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.get(url, headers=headers)


@router.put("/{thread_id}")
async def update_thread(thread_id: str, thread_data: dict, token: str):
    """
    Actualiza un hilo
    """
    url = f"{settings.threads_service_url}/v1/threads/{thread_id}"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.put(url, json=thread_data, headers=headers)


@router.delete("/{thread_id}")
async def delete_thread(thread_id: str, token: str):
    """
    Elimina un hilo
    """
    url = f"{settings.threads_service_url}/v1/threads/{thread_id}"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.delete(url, headers=headers)


@router.post("/{thread_id}/pin")
async def pin_thread(thread_id: str, token: str):
    """
    Fija un hilo importante
    """
    url = f"{settings.threads_service_url}/v1/threads/{thread_id}/pin"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.post(url, headers=headers)
