"""
Excepciones personalizadas y manejadores de errores para el servicio de archivos.
"""

from typing import Any, Dict, Optional

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.domain.models import ErrorResponse

# Importación local para evitar circular imports
def get_file_policy_error():
    """Importación lazy de FilePolicyError."""
    from app.domain.policies import FilePolicyError
    return FilePolicyError


class FileServiceError(Exception):
    """Excepción base del servicio de archivos."""
    
    def __init__(
        self, 
        message: str, 
        error_code: str, 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class FileNotFoundError(FileServiceError):
    """Error cuando no se encuentra un archivo."""
    
    def __init__(self, file_id: str):
        super().__init__(
            message=f"Archivo con ID '{file_id}' no encontrado",
            error_code="FILE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"file_id": file_id}
        )


class FileAlreadyDeletedError(FileServiceError):
    """Error cuando se intenta operar sobre un archivo ya eliminado."""
    
    def __init__(self, file_id: str):
        super().__init__(
            message=f"Archivo con ID '{file_id}' ya fue eliminado",
            error_code="FILE_ALREADY_DELETED",
            status_code=status.HTTP_410_GONE,
            details={"file_id": file_id}
        )


class StorageError(FileServiceError):
    """Error relacionado con el almacenamiento."""
    
    def __init__(self, message: str, operation: str = "unknown"):
        super().__init__(
            message=f"Error de almacenamiento: {message}",
            error_code="STORAGE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"operation": operation}
        )


class DatabaseError(FileServiceError):
    """Error relacionado con la base de datos."""
    
    def __init__(self, message: str, operation: str = "unknown"):
        super().__init__(
            message=f"Error de base de datos: {message}",
            error_code="DATABASE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"operation": operation}
        )


class EventPublishError(FileServiceError):
    """Error al publicar eventos."""
    
    def __init__(self, message: str, event_type: str = "unknown"):
        super().__init__(
            message=f"Error al publicar evento: {message}",
            error_code="EVENT_PUBLISH_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"event_type": event_type}
        )


class AuthenticationError(FileServiceError):
    """Error de autenticación."""
    
    def __init__(self, message: str = "Credenciales inválidas"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationError(FileServiceError):
    """Error de autorización."""
    
    def __init__(self, message: str = "Permisos insuficientes"):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=status.HTTP_403_FORBIDDEN
        )


class ConfigurationError(FileServiceError):
    """Error de configuración."""
    
    def __init__(self, message: str, config_key: str = "unknown"):
        super().__init__(
            message=f"Error de configuración: {message}",
            error_code="CONFIGURATION_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"config_key": config_key}
        )


# =============================================================================
# Manejadores de Errores
# =============================================================================

async def file_service_error_handler(request: Request, exc: FileServiceError) -> JSONResponse:
    """Manejador para errores del servicio de archivos."""
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.message,
            detail=str(exc.details) if exc.details else None,
            error_code=exc.error_code
        ).model_dump()
    )


async def file_policy_error_handler(request: Request, exc) -> JSONResponse:
    """Manejador para errores de políticas de archivos."""
    
    # Mapear códigos de error a códigos HTTP apropiados
    status_code_mapping = {
        "FILE_TOO_LARGE": status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        "FILE_EMPTY": status.HTTP_400_BAD_REQUEST,
        "MIME_TYPE_NOT_ALLOWED": status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        "MIME_TYPE_MISSING": status.HTTP_400_BAD_REQUEST,
        "QUOTA_EXCEEDED": status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        "FILENAME_EMPTY": status.HTTP_400_BAD_REQUEST,
        "FILENAME_TOO_LONG": status.HTTP_400_BAD_REQUEST,
        "FILENAME_INVALID_CHARS": status.HTTP_400_BAD_REQUEST,
        "FILENAME_ONLY_EXTENSION": status.HTTP_400_BAD_REQUEST,
        "CANAL_ID_REQUIRED": status.HTTP_400_BAD_REQUEST,
        "HILO_ID_REQUIRED_WITH_MESSAGE": status.HTTP_400_BAD_REQUEST,
    }
    
    status_code = status_code_mapping.get(exc.error_code, status.HTTP_400_BAD_REQUEST)
    
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            error=exc.message,
            error_code=exc.error_code
        ).model_dump()
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Manejador para errores de validación de Pydantic."""
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="Error de validación",
            detail=str(exc.errors()),
            error_code="VALIDATION_ERROR"
        ).model_dump()
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Manejador para excepciones HTTP de Starlette."""
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            error_code="HTTP_ERROR"
        ).model_dump()
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Manejador genérico para excepciones no controladas."""
    
    # En producción, no exponer detalles internos
    import os
    debug_mode = os.getenv("DEBUG", "false").lower() == "true"
    
    detail = str(exc) if debug_mode else "Error interno del servidor"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Error interno del servidor",
            detail=detail,
            error_code="INTERNAL_SERVER_ERROR"
        ).model_dump()
    )


def setup_error_handlers(app):
    """Configura todos los manejadores de errores en la aplicación FastAPI."""
    
    # Importar dinámicamente para evitar circular imports
    FilePolicyError = get_file_policy_error()
    
    # Errores específicos del servicio
    app.add_exception_handler(FileServiceError, file_service_error_handler)
    app.add_exception_handler(FilePolicyError, file_policy_error_handler)
    
    # Errores de FastAPI/Starlette
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    
    # Captura todo (debe ser el último)
    app.add_exception_handler(Exception, generic_exception_handler)