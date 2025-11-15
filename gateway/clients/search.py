"""Cliente para el servicio de Búsqueda (Grupo 8)"""
from clients.base import BaseClient
from config import settings
from typing import Optional

class SearchClient(BaseClient):
    """Cliente para interactuar con el servicio de búsqueda"""
    
    def __init__(self):
        super().__init__(settings.search_service_url)
    
    async def search(self, query: str, filters: Optional[dict] = None):
        """Buscar en todo el sistema"""
        params = {"q": query}
        if filters:
            params.update(filters)
        return await self.get("/search", params=params)
    
    async def search_messages(self, query: str, channel_id: Optional[str] = None):
        """Buscar mensajes específicamente"""
        params = {"q": query}
        if channel_id:
            params["channel_id"] = channel_id
        return await self.get("/search/messages", params=params)
    
    async def search_files(self, query: str):
        """Buscar archivos"""
        return await self.get("/search/files", params={"q": query})

# Instancia global
search_client = SearchClient()
