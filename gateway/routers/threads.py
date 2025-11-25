"""Router para hilos"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from clients.threads import threads_client

router = APIRouter()


class ThreadCreate(BaseModel):
    channel_id: str
    thread_name: str
    user_id: str


class ThreadEdit(BaseModel):
    title: Optional[str] = None
    metadata: Optional[dict] = None


@router.get("/channel/{channel_id}")
async def list_channel_threads(channel_id: str):
    result = await threads_client.list_threads_for_channel(channel_id)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result


@router.get("/mine/{user_id}")
async def list_user_threads(user_id: str):
    result = await threads_client.list_threads_for_user(user_id)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result


@router.get("/{thread_id}")
async def get_thread(thread_id: str):
    result = await threads_client.get_thread(thread_id)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result


@router.post("")
async def create_thread(payload: ThreadCreate):
    result = await threads_client.create_thread(payload.channel_id, payload.thread_name, payload.user_id)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result


@router.put("/{thread_id}")
async def edit_thread(thread_id: str, payload: ThreadEdit):
    result = await threads_client.edit_thread(thread_id, payload.title, payload.metadata)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result
