"""Cliente para el servicio de Canales (Grupo 2)"""
from clients.base import BaseClient
from config import settings

class ChannelsClient(BaseClient):
    """Cliente para interactuar con el servicio de canales"""
    
    def __init__(self):
        super().__init__(settings.channels_service_url)
    
    async def list_channels(self, page: int = 1, page_size: int = 20):
        """Listar canales paginados"""
        params = {"page": page, "page_size": page_size}
        return await self.get("/v1/channels/", params=params)
    
    async def list_channels_by_member(self, user_id: str):
        """Listar canales donde participa un usuario"""
        return await self.get(f"/v1/members/{user_id}")
    
    async def list_channels_by_owner(self, owner_id: str):
        """Listar canales por propietario"""
        return await self.get(f"/v1/members/owner/{owner_id}")
    
    async def get_channel(self, channel_id: str):
        """Obtener un canal específico"""
        return await self.get(f"/v1/channels/{channel_id}")
    
    async def create_channel(self, name: str, owner_id: str, users: list, channel_type: str = "public"):
        """Crear un nuevo canal"""
        payload = {
            "name": name,
            "owner_id": owner_id,
            "users": users,
            "channel_type": channel_type
        }
        return await self.post("/v1/channels/", json=payload)
    
    async def update_channel(self, channel_id: str, name: str = None, description: str = None):
        """Actualizar un canal"""
        payload = {}
        if name:
            payload["name"] = name
        if description:
            payload["description"] = description
        return await self.put(f"/v1/channels/{channel_id}", json=payload)
    
    async def delete_channel(self, channel_id: str):
        """Eliminar un canal"""
        return await self.delete(f"/v1/channels/{channel_id}")

# Instancia global
channels_client = ChannelsClient()
