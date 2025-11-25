"""Router para el servicio de presencia"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from clients.presence import presence_client

router = APIRouter()


class PresenceRegister(BaseModel):
    user_id: str
    device: Optional[str] = None
    ip: Optional[str] = None


class PresenceUpdate(BaseModel):
    status: Optional[str] = None
    heartbeat: Optional[bool] = False


@router.get("")
async def list_presence(status: Optional[str] = Query(None)):
    result = await presence_client.list_users(status)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result


@router.get("/stats")
async def presence_stats():
    result = await presence_client.stats()
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result


@router.get("/{user_id}")
async def get_presence(user_id: str):
    result = await presence_client.get_user(user_id)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result


@router.post("")
async def register_presence(payload: PresenceRegister):
    result = await presence_client.register(payload.user_id, payload.device, payload.ip)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result


@router.patch("/{user_id}")
async def update_presence(user_id: str, payload: PresenceUpdate):
    result = await presence_client.update_status(
        user_id,
        status=payload.status,
        heartbeat=bool(payload.heartbeat),
    )
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result


@router.delete("/{user_id}")
async def remove_presence(user_id: str):
    result = await presence_client.remove_user(user_id)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result
