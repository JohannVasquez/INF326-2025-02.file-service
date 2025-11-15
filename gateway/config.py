"""Configuración del API Gateway"""
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
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite default
        "http://localhost:8080",
        "*"  # Permitir todo en desarrollo
    ]
    
    # URLs de los microservicios
    users_service_url: str = "http://134.199.176.197/usersservice"
    channels_service_url: str = "https://channel-api-134-199-176-197.nip.io"
    messages_service_url: str = "https://messages-service.kroder.dev"
    moderation_service_url: str = "http://localhost:8001"  # Cambiar cuando tengas la URL
    files_service_url: str = "http://134.199.176.197"
    search_service_url: str = "http://localhost:8002"  # Cambiar cuando tengas la URL
    
    # Timeouts
    http_timeout: int = 30

settings = Settings()
