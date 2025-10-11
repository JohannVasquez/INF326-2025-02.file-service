"""
Dominio del servicio de archivos.

Contiene modelos de negocio, DTOs y políticas de validación.
"""

from .models import (
    FileMetadata,
    FileUploadRequest,
    UploadResponse,
    FileListItem,
    PagedFileList,
    FileEvent,
    ErrorResponse,
    HealthResponse,
    UserInfo,
)
from .policies import (
    FilePolicyValidator,
    FileSizePolicy,
    MimeTypePolicy,
    UserQuotaPolicy,
    FilenamePolicy,
    FileHashCalculator,
    IdempotencyValidator,
    FilePolicyError,
)

__all__ = [
    # Modelos y DTOs
    "FileMetadata",
    "FileUploadRequest", 
    "UploadResponse",
    "FileListItem",
    "PagedFileList",
    "FileEvent",
    "ErrorResponse",
    "HealthResponse",
    "UserInfo",
    
    # Políticas y validaciones
    "FilePolicyValidator",
    "FileSizePolicy",
    "MimeTypePolicy", 
    "UserQuotaPolicy",
    "FilenamePolicy",
    "FileHashCalculator",
    "IdempotencyValidator",
    "FilePolicyError",
]