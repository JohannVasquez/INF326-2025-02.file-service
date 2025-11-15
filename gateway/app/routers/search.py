"""
Router para Servicio de Búsqueda (Grupo 8)
Indexa y busca mensajes, hilos y archivos
"""
from fastapi import APIRouter
from typing import List, Optional
from pydantic import BaseModel
from ..client import client
from ..config import settings


router = APIRouter(prefix="/api/search", tags=["Búsqueda"])


class SearchResult(BaseModel):
    type: str  # "message", "thread", "file"
    id: str
    title: Optional[str] = None
    content: str
    channel_id: Optional[str] = None
    thread_id: Optional[str] = None
    created_at: str
    relevance_score: float


@router.get("/", response_model=List[SearchResult])
async def search(
    query: str,
    token: str,
    channel_id: Optional[str] = None,
    thread_id: Optional[str] = None,
    result_type: Optional[str] = None,  # "message", "thread", "file"
    skip: int = 0,
    limit: int = 50
):
    """
    Busca en mensajes, hilos y archivos
    """
    url = f"{settings.search_service_url}/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "q": query,
        "skip": skip,
        "limit": limit
    }
    if channel_id:
        params["channel_id"] = channel_id
    if thread_id:
        params["thread_id"] = thread_id
    if result_type:
        params["type"] = result_type
    
    return await client.get(url, headers=headers, params=params)


@router.get("/suggest")
async def search_suggestions(query: str, token: str):
    """
    Obtiene sugerencias de búsqueda
    """
    url = f"{settings.search_service_url}/v1/search/suggest"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query}
    return await client.get(url, headers=headers, params=params)


@router.post("/reindex")
async def trigger_reindex(token: str):
    """
    Trigger reindexación de contenido (admin only)
    """
    url = f"{settings.search_service_url}/v1/search/reindex"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.post(url, headers=headers)
