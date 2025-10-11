"""
Modelos de dominio y DTOs para el servicio de archivos.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class FileMetadata(BaseModel):
    """Metadatos completos de un archivo."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    canal_id: UUID
    hilo_id: Optional[UUID] = None
    mensaje_id: Optional[UUID] = None
    filename: str
    mime: str
    bytes: int
    hash_sha256: str
    version: int = 1
    storage_uri: str
    created_at: datetime
    deleted_at: Optional[datetime] = None


class FileUploadRequest(BaseModel):
    """Request para subir un archivo."""
    
    canal_id: UUID = Field(..., description="ID del canal donde se sube el archivo")
    hilo_id: Optional[UUID] = Field(None, description="ID del hilo (opcional)")
    mensaje_id: Optional[UUID] = Field(None, description="ID del mensaje (opcional)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "canal_id": "123e4567-e89b-12d3-a456-426614174000",
                "hilo_id": "123e4567-e89b-12d3-a456-426614174001",
                "mensaje_id": "123e4567-e89b-12d3-a456-426614174002"
            }
        }
    )


class UploadResponse(BaseModel):
    """Response exitoso de subida de archivo."""
    
    id: UUID
    filename: str
    mime: str
    bytes: int
    hash_sha256: str
    storage_uri: str
    created_at: datetime
    message: str = "Archivo subido exitosamente"
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "filename": "documento.pdf",
                "mime": "application/pdf",
                "bytes": 1048576,
                "hash_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "storage_uri": "s3://chat-files/2025/01/01/123e4567-e89b-12d3-a456-426614174000.pdf",
                "created_at": "2025-01-01T12:00:00Z",
                "message": "Archivo subido exitosamente"
            }
        }
    )


class FileListItem(BaseModel):
    """Item de archivo para listados."""
    
    id: UUID
    filename: str
    mime: str
    bytes: int
    created_at: datetime
    is_deleted: bool = False


class PagedFileList(BaseModel):
    """Lista paginada de archivos."""
    
    items: List[FileListItem]
    total: int
    page: int = Field(ge=1, description="Número de página (desde 1)")
    per_page: int = Field(ge=1, le=100, description="Items por página (1-100)")
    has_next: bool
    has_prev: bool
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "filename": "documento.pdf",
                        "mime": "application/pdf",
                        "bytes": 1048576,
                        "created_at": "2025-01-01T12:00:00Z",
                        "is_deleted": False
                    }
                ],
                "total": 1,
                "page": 1,
                "per_page": 20,
                "has_next": False,
                "has_prev": False
            }
        }
    )


class FileEvent(BaseModel):
    """Evento de archivo para publicación."""
    
    file_id: UUID
    canal_id: UUID
    hilo_id: Optional[UUID]
    mensaje_id: Optional[UUID]
    owner_user_id: UUID
    filename: str
    mime: str
    bytes: int
    hash_sha256: str
    created_at: datetime
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "file_id": "123e4567-e89b-12d3-a456-426614174000",
                "canal_id": "123e4567-e89b-12d3-a456-426614174001",
                "hilo_id": "123e4567-e89b-12d3-a456-426614174002",
                "mensaje_id": "123e4567-e89b-12d3-a456-426614174003",
                "owner_user_id": "123e4567-e89b-12d3-a456-426614174004",
                "filename": "documento.pdf",
                "mime": "application/pdf",
                "bytes": 1048576,
                "hash_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "created_at": "2025-01-01T12:00:00Z"
            }
        }
    )


class ErrorResponse(BaseModel):
    """Response de error estándar."""
    
    error: str
    detail: Optional[str] = None
    error_code: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "Archivo demasiado grande",
                "detail": "El archivo excede el límite de 10MB",
                "error_code": "FILE_TOO_LARGE"
            }
        }
    )


class HealthResponse(BaseModel):
    """Response del endpoint de salud."""
    
    status: str = "healthy"
    timestamp: datetime
    version: str = "1.0.0"
    services: dict = Field(default_factory=dict)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "timestamp": "2025-01-01T12:00:00Z",
                "version": "1.0.0",
                "services": {
                    "database": "healthy",
                    "storage": "healthy"
                }
            }
        }
    )


class UserInfo(BaseModel):
    """Información del usuario extraída del JWT."""
    
    user_id: UUID
    email: Optional[str] = None
    roles: List[str] = Field(default_factory=list)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "usuario@universidad.edu",
                "roles": ["student"]
            }
        }
    )