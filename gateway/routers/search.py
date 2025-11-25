"""Router para Búsqueda"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from clients.search import search_client

router = APIRouter()


def _raise_if_error(result):
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result


@router.get("")
async def search_everything(
    q: str = Query(..., description="Texto a buscar"),
    channel_id: Optional[str] = Query(None),
    thread_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
):
    messages = _raise_if_error(
        await search_client.search_messages(q, thread_id=thread_id, user_id=user_id)
    )
    files = _raise_if_error(
        await search_client.search_files(q, thread_id=thread_id)
    )
    channels = _raise_if_error(
        await search_client.search_channels(q, channel_id=channel_id, owner_id=user_id)
    )
    return {
        "channels": channels,
        "messages": messages,
        "files": files,
    }


@router.get("/messages")
async def search_messages(
    q: str = Query(..., description="Texto a buscar"),
    thread_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    message_id: Optional[str] = Query(None),
    message_type: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    result = await search_client.search_messages(
        q,
        thread_id=thread_id,
        user_id=user_id,
        message_id=message_id,
        message_type=message_type,
        limit=limit,
        offset=offset,
    )
    return _raise_if_error(result)


@router.get("/files")
async def search_files(
    q: str = Query(..., description="Texto a buscar"),
    file_id: Optional[str] = Query(None),
    thread_id: Optional[str] = Query(None),
    message_id: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    result = await search_client.search_files(
        q,
        file_id=file_id,
        thread_id=thread_id,
        message_id=message_id,
        limit=limit,
        offset=offset,
    )
    return _raise_if_error(result)


@router.get("/channels")
async def search_channels(
    q: str = Query(..., description="Texto a buscar"),
    channel_id: Optional[str] = Query(None),
    owner_id: Optional[str] = Query(None),
    channel_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    result = await search_client.search_channels(
        q,
        channel_id=channel_id,
        owner_id=owner_id,
        channel_type=channel_type,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )
    return _raise_if_error(result)
