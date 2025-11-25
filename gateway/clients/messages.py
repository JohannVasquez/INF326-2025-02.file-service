"""Cliente para el servicio de Mensajes (Grupo 4)"""
from clients.base import BaseClient
from config import settings
from typing import Optional, Dict, Any, List

class MessagesClient(BaseClient):
    """Cliente para interactuar con el servicio de mensajes"""
    
    def __init__(self):
        super().__init__(settings.messages_service_url)
    
    async def list_messages(
        self, 
        thread_id: str,
        limit: int = 50,
        cursor: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Lista mensajes de un thread.
        
        Args:
            thread_id: ID del thread (UUID, requerido)
            limit: Número máximo de mensajes (1-200, default 50)
            cursor: Cursor para paginación (opcional)
        """
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return await self.get(f"/threads/{thread_id}/messages", params=params)
    
    async def get_message(self, thread_id: str, message_id: str) -> Dict[str, Any]:
        """Obtener un mensaje específico de un thread"""
        return await self.get(f"/threads/{thread_id}/messages/{message_id}")
    
    async def create_message(
        self,
        thread_id: str,
        content: str,
        message_type: Optional[str] = None,
        paths: Optional[List[str]] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Crear un nuevo mensaje en un thread.
        
        Args:
            thread_id: ID del thread (UUID, requerido en path)
            content: Contenido del mensaje (requerido)
            message_type: Tipo de mensaje - 'text', 'audio', 'file' (opcional)
            paths: Lista de rutas asociadas al mensaje (opcional)
        """
        payload = {"content": content}
        if message_type:
            payload["type"] = message_type
        if paths:
            payload["paths"] = paths
        headers = {"X-User-Id": user_id} if user_id else None
        return await self.post(
            f"/threads/{thread_id}/messages",
            json=payload,
            headers=headers,
        )
    
    async def update_message(
        self,
        thread_id: str,
        message_id: str,
        content: str,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Actualizar un mensaje existente"""
        headers = {"X-User-Id": user_id} if user_id else None
        return await self.put(
            f"/threads/{thread_id}/messages/{message_id}",
            json={"content": content},
            headers=headers,
        )
    
    async def delete_message(
        self,
        thread_id: str,
        message_id: str,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Eliminar un mensaje de un thread"""
        headers = {"X-User-Id": user_id} if user_id else None
        return await self.delete(
            f"/threads/{thread_id}/messages/{message_id}",
            headers=headers,
        )

# Instancia global
messages_client = MessagesClient()
