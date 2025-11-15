"""
Router para Servicio de Canales (Grupo 2)
Creación y administración de canales
"""
from fastapi import APIRouter
from typing import List, Optional
from pydantic import BaseModel
from ..client import client
from ..config import settings


router = APIRouter(prefix="/api/channels", tags=["Canales"])


class ChannelCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_private: bool = False
    subject: Optional[str] = None  # Para canales por asignatura


class Channel(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    is_private: bool
    subject: Optional[str] = None
    created_by: str
    created_at: str
    members_count: int


@router.post("/", response_model=Channel)
async def create_channel(channel: ChannelCreate, token: str):
    """
    Crea un nuevo canal
    """
    url = f"{settings.channels_service_url}/v1/channels"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.post(url, json=channel.dict(), headers=headers)


@router.get("/", response_model=List[Channel])
async def list_channels(
    token: str,
    skip: int = 0,
    limit: int = 50,
    subject: Optional[str] = None
):
    """
    Lista canales disponibles
    """
    url = f"{settings.channels_service_url}/v1/channels"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"skip": skip, "limit": limit}
    if subject:
        params["subject"] = subject
    return await client.get(url, headers=headers, params=params)


@router.get("/{channel_id}", response_model=Channel)
async def get_channel(channel_id: str, token: str):
    """
    Obtiene detalles de un canal
    """
    url = f"{settings.channels_service_url}/v1/channels/{channel_id}"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.get(url, headers=headers)


@router.put("/{channel_id}")
async def update_channel(channel_id: str, channel_data: dict, token: str):
    """
    Actualiza información de un canal
    """
    url = f"{settings.channels_service_url}/v1/channels/{channel_id}"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.put(url, json=channel_data, headers=headers)


@router.delete("/{channel_id}")
async def delete_channel(channel_id: str, token: str):
    """
    Elimina un canal
    """
    url = f"{settings.channels_service_url}/v1/channels/{channel_id}"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.delete(url, headers=headers)


@router.post("/{channel_id}/members/{user_id}")
async def add_member(channel_id: str, user_id: str, token: str):
    """
    Agrega un miembro al canal
    """
    url = f"{settings.channels_service_url}/v1/channels/{channel_id}/members"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.post(url, json={"user_id": user_id}, headers=headers)


@router.get("/{channel_id}/members")
async def list_members(channel_id: str, token: str):
    """
    Lista miembros de un canal
    """
    url = f"{settings.channels_service_url}/v1/channels/{channel_id}/members"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.get(url, headers=headers)
