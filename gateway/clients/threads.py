"""Cliente para el servicio de Threads"""
from typing import Optional
from clients.base import BaseClient
from config import settings


class ThreadsClient(BaseClient):
    """Cliente HTTP para administrar hilos"""

    def __init__(self):
        super().__init__(settings.threads_service_url)

    async def list_threads_for_channel(self, channel_id: str):
        return await self.get("/channel/get_threads", params={"channel_id": channel_id})

    async def list_threads_for_user(self, user_id: str):
        return await self.get(f"/threads/mine/{user_id}")

    async def create_thread(self, channel_id: str, thread_name: str, user_id: str):
        params = {
            "channel_id": channel_id,
            "thread_name": thread_name,
            "user_id": user_id,
        }
        return await self.post("/threads/", params=params)

    async def get_thread(self, thread_id: str):
        return await self.get(f"/threads/{thread_id}")

    async def edit_thread(self, thread_id: str, title: Optional[str] = None, metadata: Optional[dict] = None):
        payload = {}
        if title is not None:
            payload["title"] = title
        if metadata is not None:
            payload["metadata"] = metadata
        return await self.put(f"/threads/{thread_id}/edit", json=payload)


threads_client = ThreadsClient()
