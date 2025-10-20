import json
import asyncio
import aio_pika
from .config import settings

class EventBus:
    def __init__(self):
        self._conn = None
        self._channel = None
        self._exchange = None

    async def connect(self):
        if self._conn:
            return
        self._conn = await aio_pika.connect_robust(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            login=settings.rabbitmq_user,
            password=settings.rabbitmq_password,
        )
        self._channel = await self._conn.channel()
        self._exchange = await self._channel.declare_exchange(settings.rabbitmq_exchange, aio_pika.ExchangeType.TOPIC, durable=True)

    async def publish(self, routing_key: str, payload: dict):
        await self.connect()
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        message = aio_pika.Message(body=body, content_type="application/json")
        await self._exchange.publish(message, routing_key=routing_key)

event_bus = EventBus()
