"""
Router para Servicio de Presencia (Grupo 5)
Administra estados de conexión de usuarios
"""
from fastapi import APIRouter
from typing import List
from pydantic import BaseModel
from ..client import client
from ..config import settings


router = APIRouter(prefix="/api/presence", tags=["Presencia"])


class PresenceStatus(BaseModel):
    user_id: str
    status: str  # "online", "offline", "away", "busy"
    last_seen: str


@router.post("/status")
async def update_status(status: str, token: str):
    """
    Actualiza el estado de presencia del usuario actual
    """
    url = f"{settings.presence_service_url}/v1/presence/status"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.post(url, json={"status": status}, headers=headers)


@router.get("/users/{user_id}", response_model=PresenceStatus)
async def get_user_status(user_id: str, token: str):
    """
    Obtiene el estado de presencia de un usuario
    """
    url = f"{settings.presence_service_url}/v1/presence/users/{user_id}"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.get(url, headers=headers)


@router.get("/channel/{channel_id}", response_model=List[PresenceStatus])
async def get_channel_presence(channel_id: str, token: str):
    """
    Obtiene usuarios online en un canal
    """
    url = f"{settings.presence_service_url}/v1/presence/channel/{channel_id}"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.get(url, headers=headers)
