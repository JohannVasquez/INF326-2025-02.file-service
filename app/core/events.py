"""
Sistema de eventos para el servicio de archivos.
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4

import structlog

from app.core.config import settings
from app.domain.models import FileEvent


logger = structlog.get_logger(__name__)


class EventPublisher(ABC):
    """Interfaz abstracta para publicadores de eventos."""
    
    @abstractmethod
    async def publish(self, event_type: str, payload: Dict[str, Any]) -> bool:
        """
        Publica un evento.
        
        Args:
            event_type: Tipo del evento
            payload: Datos del evento
            
        Returns:
            bool: True si se publicó exitosamente, False si no
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Verifica la salud del publisher.
        
        Returns:
            bool: True si está saludable, False si no
        """
        pass


class NoOpEventPublisher(EventPublisher):
    """Publisher que no hace nada (para desarrollo/testing)."""
    
    async def publish(self, event_type: str, payload: Dict[str, Any]) -> bool:
        """Simula la publicación logueando el evento."""
        logger.info(
            "Event published (no-op)",
            event_type=event_type,
            payload=payload
        )
        return True
    
    async def health_check(self) -> bool:
        """Siempre está saludable."""
        return True


class RedisEventPublisher(EventPublisher):
    """Publisher de eventos usando Redis Streams."""
    
    def __init__(self, redis_url: str, stream_name: str):
        self.redis_url = redis_url
        self.stream_name = stream_name
        self._redis = None
    
    async def _get_redis(self):
        """Obtiene la conexión a Redis (lazy loading)."""
        if self._redis is None:
            try:
                import redis.asyncio as redis
                self._redis = redis.from_url(self.redis_url)
            except ImportError:
                logger.error("Redis library not installed")
                raise ImportError("redis library is required for RedisEventPublisher")
        return self._redis
    
    async def publish(self, event_type: str, payload: Dict[str, Any]) -> bool:
        """Publica un evento en Redis Stream."""
        try:
            redis_client = await self._get_redis()
            
            # Preparar el evento con metadatos
            event_data = {
                "event_id": str(uuid4()),
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "payload": json.dumps(payload, default=str),
                "service": "filesvc"
            }
            
            # Publicar en Redis Stream
            await redis_client.xadd(self.stream_name, event_data)
            
            logger.info(
                "Event published to Redis",
                event_type=event_type,
                stream=self.stream_name,
                event_id=event_data["event_id"]
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "Failed to publish event to Redis",
                event_type=event_type,
                error=str(e),
                stream=self.stream_name
            )
            return False
    
    async def health_check(self) -> bool:
        """Verifica la conexión a Redis."""
        try:
            redis_client = await self._get_redis()
            await redis_client.ping()
            return True
        except Exception as e:
            logger.error("Redis health check failed", error=str(e))
            return False


class EventService:
    """Servicio central de eventos."""
    
    def __init__(self, publisher: EventPublisher):
        self.publisher = publisher
    
    async def publish_file_added(self, file_event: FileEvent) -> bool:
        """
        Publica un evento de archivo agregado.
        
        Args:
            file_event: Datos del evento de archivo
            
        Returns:
            bool: True si se publicó exitosamente
        """
        payload = file_event.model_dump()
        
        # Convertir datetime a string para serialización
        if "created_at" in payload:
            payload["created_at"] = payload["created_at"].isoformat()
        
        return await self.publisher.publish("files.added", payload)
    
    async def publish_file_deleted(
        self, 
        file_id: str, 
        user_id: str, 
        canal_id: str,
        hilo_id: Optional[str] = None,
        mensaje_id: Optional[str] = None
    ) -> bool:
        """
        Publica un evento de archivo eliminado.
        
        Args:
            file_id: ID del archivo eliminado
            user_id: ID del usuario que eliminó
            canal_id: ID del canal
            hilo_id: ID del hilo (opcional)
            mensaje_id: ID del mensaje (opcional)
            
        Returns:
            bool: True si se publicó exitosamente
        """
        payload = {
            "file_id": file_id,
            "user_id": user_id,
            "canal_id": canal_id,
            "hilo_id": hilo_id,
            "mensaje_id": mensaje_id,
            "deleted_at": datetime.utcnow().isoformat()
        }
        
        return await self.publisher.publish("files.deleted", payload)
    
    async def health_check(self) -> bool:
        """Verifica la salud del servicio de eventos."""
        return await self.publisher.health_check()


# Factory para crear el publisher apropiado
def create_event_publisher() -> EventPublisher:
    """Crea el publisher de eventos según la configuración."""
    
    if settings.events_broker_kind == "redis":
        return RedisEventPublisher(
            redis_url=settings.redis_url,
            stream_name=settings.events_stream_name
        )
    elif settings.events_broker_kind == "noop":
        return NoOpEventPublisher()
    else:
        logger.warning(
            "Unknown events_broker_kind, falling back to no-op",
            broker_kind=settings.events_broker_kind
        )
        return NoOpEventPublisher()


# Instancia global del servicio de eventos
_event_service: Optional[EventService] = None


def get_event_service() -> EventService:
    """Obtiene la instancia del servicio de eventos."""
    global _event_service
    
    if _event_service is None:
        publisher = create_event_publisher()
        _event_service = EventService(publisher)
    
    return _event_service


# Utility functions para uso directo
async def publish_file_added(file_event: FileEvent) -> bool:
    """Función utilitaria para publicar evento de archivo agregado."""
    event_service = get_event_service()
    return await event_service.publish_file_added(file_event)


async def publish_file_deleted(
    file_id: str,
    user_id: str, 
    canal_id: str,
    hilo_id: Optional[str] = None,
    mensaje_id: Optional[str] = None
) -> bool:
    """Función utilitaria para publicar evento de archivo eliminado."""
    event_service = get_event_service()
    return await event_service.publish_file_deleted(
        file_id=file_id,
        user_id=user_id,
        canal_id=canal_id,
        hilo_id=hilo_id,
        mensaje_id=mensaje_id
    )