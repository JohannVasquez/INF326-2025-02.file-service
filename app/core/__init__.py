"""
Core del servicio de archivos.

Contiene configuración, seguridad, eventos y manejo de errores.
"""

from .config import settings, Settings
from .security import (
    get_current_user,
    get_optional_user,
    JWTValidator,
    PermissionChecker,
    AuthenticationError,
    AuthorizationError,
)
from .events import (
    get_event_service,
    publish_file_added,
    publish_file_deleted,
    EventService,
    EventPublisher,
)
from .errors import (
    FileServiceError,
    FileNotFoundError,
    FileAlreadyDeletedError,
    StorageError,
    DatabaseError,
    setup_error_handlers,
)

__all__ = [
    # Configuración
    "settings",
    "Settings",
    
    # Seguridad
    "get_current_user",
    "get_optional_user",
    "JWTValidator",
    "PermissionChecker",
    "AuthenticationError",
    "AuthorizationError",
    
    # Eventos
    "get_event_service",
    "publish_file_added",
    "publish_file_deleted",
    "EventService",
    "EventPublisher",
    
    # Errores
    "FileServiceError",
    "FileNotFoundError",
    "FileAlreadyDeletedError",
    "StorageError",
    "DatabaseError",
    "setup_error_handlers",
]