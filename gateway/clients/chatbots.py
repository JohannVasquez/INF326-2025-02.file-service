"""Clientes para los chatbots externos"""
from clients.base import BaseClient
from config import settings


class WikipediaChatClient(BaseClient):
    def __init__(self):
        super().__init__(settings.wikipedia_service_url)

    async def ask(self, message: str):
        return await self.post("/chat-wikipedia", json={"message": message})


class ProgrammingChatClient(BaseClient):
    def __init__(self):
        super().__init__(settings.chatbot_programming_service_url)

    async def ask(self, message: str):
        return await self.post("/chat", json={"message": message})


wikipedia_chat_client = WikipediaChatClient()
programming_chat_client = ProgrammingChatClient()
