"""Cliente para el servicio de Moderación (Grupo 6)"""
from clients.base import BaseClient
from config import settings
from typing import Optional

class ModerationClient(BaseClient):
    """Cliente para interactuar con el servicio de moderación"""
    
    def __init__(self):
        super().__init__(settings.moderation_service_url)
        self.api_key = None  # Se puede configurar si es necesario
    
    def _get_headers(self):
        """Headers con API Key si está configurada"""
        if self.api_key:
            return {"X-API-Key": self.api_key}
        return None
    
    async def check_message(self, user_id: str, channel_id: str, content: str):
        """Moderar un mensaje"""
        payload = {
            "user_id": user_id,
            "channel_id": channel_id,
            "content": content
        }
        return await self.post("/api/v1/moderation/check", json=payload)
    
    async def analyze_text(self, text: str):
        """Analizar texto para moderación"""
        return await self.post("/api/v1/moderation/analyze", json={"text": text})
    
    async def get_user_status(self, user_id: str, channel_id: str):
        """Obtener estado de moderación de un usuario"""
        return await self.get(f"/api/v1/moderation/status/{user_id}/{channel_id}")
    
    async def list_banned_users(self):
        """Listar usuarios baneados (requiere API Key)"""
        return await self.get("/api/v1/admin/banned-users", headers=self._get_headers())
    
    async def get_user_violations(self, user_id: str):
        """Obtener historial de violaciones de un usuario (requiere API Key)"""
        return await self.get(f"/api/v1/admin/users/{user_id}/violations", headers=self._get_headers())
    
    async def unban_user(self, user_id: str):
        """Desbanear un usuario (requiere API Key)"""
        return await self.put(f"/api/v1/admin/users/{user_id}/unban", headers=self._get_headers())
    
    async def list_blacklist_words(self):
        """Listar palabras de la lista negra"""
        return await self.get("/api/v1/blacklist/words")
    
    async def add_blacklist_word(self, word: str):
        """Agregar palabra a lista negra (requiere API Key)"""
        return await self.post("/api/v1/blacklist/words", json={"word": word}, headers=self._get_headers())

# Instancia global
moderation_client = ModerationClient()
