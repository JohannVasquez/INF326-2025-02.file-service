"""Router para Búsqueda"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from clients.search import search_client

router = APIRouter()

@router.get("")
async def search(
    q: str = Query(..., description="Query de búsqueda"),
    channel_id: Optional[str] = Query(None)
):
    """Búsqueda general"""
    filters = {"channel_id": channel_id} if channel_id else None
    result = await search_client.search(q, filters)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result

@router.get("/messages")
async def search_messages(
    q: str = Query(..., description="Query de búsqueda"),
    channel_id: Optional[str] = Query(None)
):
    """Buscar mensajes"""
    result = await search_client.search_messages(q, channel_id)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result

@router.get("/files")
async def search_files(q: str = Query(..., description="Query de búsqueda")):
    """Buscar archivos"""
    result = await search_client.search_files(q)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result
