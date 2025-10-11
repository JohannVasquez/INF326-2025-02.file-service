"""
Configuración del servicio de archivos usando pydantic-settings.
"""

from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración del servicio de archivos."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # =============================================================================
    # Configuración de Archivos
    # =============================================================================
    files_max_bytes: int = Field(
        default=10485760,  # 10MB
        description="Tamaño máximo de archivo en bytes"
    )
    
    files_allowed_mime: List[str] = Field(
        default=[
            "image/png", "image/jpeg", "image/gif", "image/webp",
            "application/pdf", "text/plain", "text/markdown",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ],
        description="Tipos MIME permitidos"
    )
    
    files_user_quota_bytes: int = Field(
        default=104857600,  # 100MB
        description="Cuota por usuario en bytes"
    )
    
    # =============================================================================
    # Base de Datos
    # =============================================================================
    db_url: str = Field(
        default="postgresql+asyncpg://files_user:files_pass@localhost:5432/files_db",
        description="URL de conexión a la base de datos"
    )
    
    db_pool_size: int = Field(
        default=10,
        description="Tamaño del pool de conexiones"
    )
    
    db_max_overflow: int = Field(
        default=20,
        description="Máximo overflow del pool"
    )
    
    # =============================================================================
    # Almacenamiento
    # =============================================================================
    storage_kind: str = Field(
        default="s3",
        description="Tipo de almacenamiento: 's3' o 'local'"
    )
    
    # Para almacenamiento local
    local_base_path: str = Field(
        default="/data/files",
        description="Ruta base para almacenamiento local"
    )
    
    # Para almacenamiento S3/MinIO
    s3_endpoint_url: Optional[str] = Field(
        default="http://localhost:9000",
        description="URL del endpoint S3/MinIO"
    )
    
    s3_region: str = Field(
        default="us-east-1",
        description="Región de S3"
    )
    
    s3_bucket: str = Field(
        default="chat-files",
        description="Bucket de S3"
    )
    
    s3_access_key: str = Field(
        default="user",
        description="Access key de S3"
    )
    
    s3_secret_key: str = Field(
        default="1234",
        description="Secret key de S3"
    )
    
    s3_use_ssl: bool = Field(
        default=False,
        description="Usar SSL para S3"
    )
    
    s3_presigned_url_expiry: int = Field(
        default=3600,  # 1 hora
        description="Tiempo de expiración de URLs prefirmadas en segundos"
    )
    
    # =============================================================================
    # Seguridad
    # =============================================================================
    jwt_public_key_pem: str = Field(
        default="",
        description="Clave pública para validar JWTs en formato PEM"
    )
    
    jwt_algorithm: str = Field(
        default="RS256",
        description="Algoritmo para validar JWTs"
    )
    
    # =============================================================================
    # Mensajería/Eventos
    # =============================================================================
    events_broker_kind: str = Field(
        default="noop",
        description="Tipo de broker: 'redis' o 'noop'"
    )
    
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="URL de conexión a Redis"
    )
    
    events_stream_name: str = Field(
        default="files_events",
        description="Nombre del stream de eventos"
    )
    
    events_consumer_group: str = Field(
        default="filesvc_group",
        description="Grupo de consumidores"
    )
    
    # =============================================================================
    # Observabilidad
    # =============================================================================
    log_level: str = Field(
        default="INFO",
        description="Nivel de logging"
    )
    
    log_format: str = Field(
        default="json",
        description="Formato de logs: 'json' o 'text'"
    )
    
    enable_metrics: bool = Field(
        default=False,
        description="Habilitar métricas Prometheus"
    )
    
    metrics_port: int = Field(
        default=9090,
        description="Puerto para métricas"
    )
    
    # =============================================================================
    # API
    # =============================================================================
    api_host: str = Field(
        default="0.0.0.0",
        description="Host del servidor API"
    )
    
    api_port: int = Field(
        default=8000,
        description="Puerto del servidor API"
    )
    
    api_workers: int = Field(
        default=1,
        description="Número de workers"
    )
    
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Orígenes permitidos para CORS"
    )
    
    cors_allow_credentials: bool = Field(
        default=True,
        description="Permitir credenciales en CORS"
    )
    
    rate_limit_requests: int = Field(
        default=100,
        description="Requests por minuto"
    )
    
    rate_limit_window: int = Field(
        default=60,
        description="Ventana de rate limiting en segundos"
    )
    
    # =============================================================================
    # Desarrollo
    # =============================================================================
    debug: bool = Field(
        default=True,
        description="Modo debug"
    )
    
    auto_reload: bool = Field(
        default=True,
        description="Auto-reload en desarrollo"
    )
    
    show_docs: bool = Field(
        default=True,
        description="Mostrar documentación automática"
    )
    
    @field_validator("files_allowed_mime", mode="before")
    @classmethod
    def parse_mime_types(cls, v):
        """Parsea tipos MIME desde string separado por comas."""
        if isinstance(v, str):
            return [mime.strip() for mime in v.split(",") if mime.strip()]
        return v
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parsea orígenes CORS desde string separado por comas."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    @field_validator("storage_kind")
    @classmethod
    def validate_storage_kind(cls, v):
        """Valida que el tipo de almacenamiento sea válido."""
        if v not in ["s3", "local"]:
            raise ValueError("storage_kind debe ser 's3' o 'local'")
        return v
    
    @field_validator("events_broker_kind")
    @classmethod
    def validate_broker_kind(cls, v):
        """Valida que el tipo de broker sea válido."""
        if v not in ["redis", "noop"]:
            raise ValueError("events_broker_kind debe ser 'redis' o 'noop'")
        return v
    
    @field_validator("log_format")
    @classmethod
    def validate_log_format(cls, v):
        """Valida que el formato de log sea válido."""
        if v not in ["json", "text"]:
            raise ValueError("log_format debe ser 'json' o 'text'")
        return v
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Valida que el nivel de log sea válido."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level debe ser uno de: {', '.join(valid_levels)}")
        return v.upper()


# Instancia global de configuración
settings = Settings()