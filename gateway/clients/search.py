"""Cliente para el servicio de Búsqueda (Grupo 8)"""
from clients.base import BaseClient
from config import settings
from typing import Optional, Dict, Any

class SearchClient(BaseClient):
    """Cliente para interactuar con el servicio de búsqueda"""
    
    def __init__(self):
        super().__init__(settings.search_service_url)
    
    def _build_params(self, query: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = {"q": query}
        if extra:
            params.update({k: v for k, v in extra.items() if v is not None})
        return params

    async def search_messages(
        self,
        query: str,
        *,
        user_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        message_id: Optional[str] = None,
        message_type: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ):
        params = self._build_params(
            query,
            {
                "user_id": user_id,
                "thread_id": thread_id,
                "message_id": message_id,
                "type_": message_type,
                "limit": limit,
                "offset": offset,
            },
        )
        return await self.get("/api/message/search_message", params=params)

    async def search_files(
        self,
        query: str,
        *,
        file_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        message_id: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ):
        params = self._build_params(
            query,
            {
                "file_id": file_id,
                "thread_id": thread_id,
                "message_id": message_id,
                "limit": limit,
                "offset": offset,
            },
        )
        return await self.get("/api/files/search_files", params=params)

    async def search_channels(
        self,
        query: str,
        *,
        channel_id: Optional[str] = None,
        owner_id: Optional[str] = None,
        channel_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: int = 10,
        offset: int = 0,
    ):
        params = self._build_params(
            query,
            {
                "channel_id": channel_id,
                "owner_id": owner_id,
                "channel_type": channel_type,
                "is_active": is_active,
                "limit": limit,
                "offset": offset,
            },
        )
        return await self.get("/api/channel/search_channel", params=params)

# Instancia global
search_client = SearchClient()
