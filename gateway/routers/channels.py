"""Router para Canales"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from clients.channels import channels_client

router = APIRouter()

class ChannelCreate(BaseModel):
    name: str
    owner_id: str
    users: list
    channel_type: str = "public"

class ChannelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


@router.get("")
async def list_channels(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    """Listar canales paginados"""
    result = await channels_client.list_channels(page, page_size)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result


@router.get("/member/{user_id}")
async def list_channels_by_member(user_id: str):
    """Listar canales donde participa un usuario"""
    result = await channels_client.list_channels_by_member(user_id)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result

@router.get("/owner/{owner_id}")
async def list_channels_by_owner(owner_id: str):
    """Listar canales por propietario"""
    result = await channels_client.list_channels_by_owner(owner_id)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result

@router.get("/{channel_id}")
async def get_channel(channel_id: str):
    """Obtener un canal específico"""
    result = await channels_client.get_channel(channel_id)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 404), detail=result)
    return result

@router.post("")
async def create_channel(channel: ChannelCreate):
    """Crear un nuevo canal"""
    result = await channels_client.create_channel(
        channel.name, 
        channel.owner_id, 
        channel.users,
        channel.channel_type
    )
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result

@router.put("/{channel_id}")
async def update_channel(channel_id: str, channel: ChannelUpdate):
    """Actualizar un canal"""
    result = await channels_client.update_channel(channel_id, channel.name, channel.description)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result

@router.delete("/{channel_id}")
async def delete_channel(channel_id: str):
    """Eliminar un canal"""
    result = await channels_client.delete_channel(channel_id)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result
