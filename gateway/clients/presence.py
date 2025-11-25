"""Cliente para el servicio de Presencia"""
from typing import Optional
from clients.base import BaseClient
from config import settings


class PresenceClient(BaseClient):
    """Cliente HTTP para el servicio de presencia"""

    def __init__(self):
        super().__init__(settings.presence_service_url)

    async def register(self, user_id: str, device: Optional[str] = None, ip: Optional[str] = None):
        payload = {"userId": user_id}
        if device:
            payload["device"] = device
        if ip:
            payload["ip"] = ip
        return await self.post("/presence", json=payload)

    async def list_users(self, status: Optional[str] = None):
        params = {"status": status} if status else None
        return await self.get("/presence", params=params)

    async def get_user(self, user_id: str):
        return await self.get(f"/presence/{user_id}")

    async def update_status(self, user_id: str, status: Optional[str] = None, heartbeat: bool = False):
        payload = {}
        if status:
            payload["status"] = status
        if heartbeat:
            payload["heartbeat"] = True
        return await self.patch(f"/presence/{user_id}", json=payload)

    async def stats(self):
        return await self.get("/presence/stats")

    async def remove_user(self, user_id: str):
        return await self.delete(f"/presence/{user_id}")


presence_client = PresenceClient()
