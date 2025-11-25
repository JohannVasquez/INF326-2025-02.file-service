"""Configuración del API Gateway"""
from __future__ import annotations

import json

from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"  # Ignorar variables de entorno adicionales
    )
    
    # Gateway
    app_name: str = "api-gateway"
    app_env: str = "production"
    app_port: int = 8000
    
    # CORS (se guarda como string crudo para evitar json.loads implícito)
    cors_origins_raw: str = ",".join(
        [
            "http://localhost:3000",
            "http://localhost:5173",  # Vite default
            "http://localhost:8080",
            "*",  # Permitir todo en desarrollo
        ]
    )

    @property
    def cors_origins(self) -> List[str]:
        value = (self.cors_origins_raw or "").strip()
        if not value:
            return ["*"]
        if value.startswith("["):
            try:
                data = json.loads(value)
                if isinstance(data, list):
                    return [str(origin).strip() for origin in data if str(origin).strip()]
            except json.JSONDecodeError:
                pass
        return [origin.strip() for origin in value.split(",") if origin.strip()]
    
    # URLs de los microservicios
    users_service_url: str = "https://users.inf326.nursoft.dev/usersservice"
    channels_service_url: str = "https://channel-api-134-199-176-197.nip.io"
    messages_service_url: str = "https://messages-service.kroder.dev"
    moderation_service_url: str = "https://moderation.inf326.nur.dev"
    files_service_url: str = "http://134.199.176.197"
    search_service_url: str = "https://searchservice.inf326.nursoft.dev"
    threads_service_url: str = "https://threads.inf326.nursoft.dev"
    presence_service_url: str = "https://presence-134-199-176-197.nip.io/api/v1.0.0"
    wikipedia_service_url: str = "http://wikipedia-chatbot-134-199-176-197.nip.io"
    chatbot_programming_service_url: str = "https://chatbotprogra.inf326.nursoft.dev"
    
    # Timeouts
    http_timeout: int = 30

settings = Settings()
