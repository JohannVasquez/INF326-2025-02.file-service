"""
Políticas y validaciones de negocio para el servicio de archivos.
"""

import hashlib
from typing import BinaryIO, List, Optional, TYPE_CHECKING
from uuid import UUID

# Importación condicional para evitar circular imports
if TYPE_CHECKING:
    from app.core.config import Settings


class FilePolicyError(Exception):
    """Error de validación de políticas de archivos."""
    
    def __init__(self, message: str, error_code: str):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class FileSizePolicy:
    """Política de tamaño de archivos."""
    
    def __init__(self, max_bytes: int):
        self.max_bytes = max_bytes
    
    def validate(self, file_size: int) -> None:
        """Valida que el archivo no exceda el tamaño máximo."""
        if file_size > self.max_bytes:
            raise FilePolicyError(
                f"El archivo excede el tamaño máximo permitido de {self.max_bytes:,} bytes",
                "FILE_TOO_LARGE"
            )
        
        if file_size <= 0:
            raise FilePolicyError(
                "El archivo está vacío",
                "FILE_EMPTY"
            )


class MimeTypePolicy:
    """Política de tipos MIME permitidos."""
    
    def __init__(self, allowed_mimes: List[str]):
        self.allowed_mimes = {mime.lower().strip() for mime in allowed_mimes}
    
    def validate(self, mime_type: str) -> None:
        """Valida que el tipo MIME esté permitido."""
        if not mime_type:
            raise FilePolicyError(
                "Tipo MIME no especificado",
                "MIME_TYPE_MISSING"
            )
        
        mime_lower = mime_type.lower().strip()
        if mime_lower not in self.allowed_mimes:
            raise FilePolicyError(
                f"Tipo MIME '{mime_type}' no permitido. Tipos válidos: {', '.join(sorted(self.allowed_mimes))}",
                "MIME_TYPE_NOT_ALLOWED"
            )


class UserQuotaPolicy:
    """Política de cuota por usuario."""
    
    def __init__(self, quota_bytes: int):
        self.quota_bytes = quota_bytes
    
    def validate(self, current_usage: int, new_file_size: int) -> None:
        """Valida que el usuario no exceda su cuota."""
        if current_usage + new_file_size > self.quota_bytes:
            available = max(0, self.quota_bytes - current_usage)
            raise FilePolicyError(
                f"Cuota excedida. Espacio disponible: {available:,} bytes, archivo: {new_file_size:,} bytes",
                "QUOTA_EXCEEDED"
            )


class FilenamePolicy:
    """Política de nombres de archivo."""
    
    # Caracteres no permitidos en nombres de archivo
    FORBIDDEN_CHARS = {'/', '\\', ':', '*', '?', '"', '<', '>', '|', '\0'}
    MAX_FILENAME_LENGTH = 255
    
    def validate(self, filename: str) -> None:
        """Valida que el nombre de archivo sea válido."""
        if not filename or not filename.strip():
            raise FilePolicyError(
                "Nombre de archivo vacío",
                "FILENAME_EMPTY"
            )
        
        filename = filename.strip()
        
        if len(filename) > self.MAX_FILENAME_LENGTH:
            raise FilePolicyError(
                f"Nombre de archivo demasiado largo (máximo {self.MAX_FILENAME_LENGTH} caracteres)",
                "FILENAME_TOO_LONG"
            )
        
        if any(char in filename for char in self.FORBIDDEN_CHARS):
            raise FilePolicyError(
                f"Nombre de archivo contiene caracteres no permitidos: {', '.join(self.FORBIDDEN_CHARS)}",
                "FILENAME_INVALID_CHARS"
            )
        
        # Validar que no sea solo extensión
        if filename.startswith('.') and '.' not in filename[1:]:
            raise FilePolicyError(
                "Nombre de archivo no puede ser solo una extensión",
                "FILENAME_ONLY_EXTENSION"
            )


class FileHashCalculator:
    """Calculadora de hash SHA256 para archivos."""
    
    @staticmethod
    def calculate_sha256(file_content: bytes) -> str:
        """Calcula el hash SHA256 de un archivo."""
        return hashlib.sha256(file_content).hexdigest()
    
    @staticmethod
    def calculate_sha256_stream(file_stream: BinaryIO) -> str:
        """Calcula el hash SHA256 de un stream de archivo."""
        sha256_hash = hashlib.sha256()
        
        # Procesar en chunks para archivos grandes
        for chunk in iter(lambda: file_stream.read(8192), b""):
            sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()


class FilePolicyValidator:
    """Validador central de políticas de archivos."""
    
    def __init__(self, settings: "Settings"):
        self.size_policy = FileSizePolicy(settings.files_max_bytes)
        self.mime_policy = MimeTypePolicy(settings.files_allowed_mime)
        self.quota_policy = UserQuotaPolicy(settings.files_user_quota_bytes)
        self.filename_policy = FilenamePolicy()
    
    def validate_upload(
        self,
        filename: str,
        file_size: int,
        mime_type: str,
        user_current_usage: int = 0
    ) -> None:
        """Valida todos los aspectos de una subida de archivo."""
        
        # Validar nombre de archivo
        self.filename_policy.validate(filename)
        
        # Validar tamaño
        self.size_policy.validate(file_size)
        
        # Validar tipo MIME
        self.mime_policy.validate(mime_type)
        
        # Validar cuota de usuario
        self.quota_policy.validate(user_current_usage, file_size)
    
    def validate_file_associations(
        self,
        canal_id: UUID,
        hilo_id: Optional[UUID] = None,
        mensaje_id: Optional[UUID] = None
    ) -> None:
        """Valida las asociaciones de archivo."""
        
        if not canal_id:
            raise FilePolicyError(
                "ID de canal es obligatorio",
                "CANAL_ID_REQUIRED"
            )
        
        # Si hay mensaje_id, debe haber hilo_id (regla de negocio)
        if mensaje_id and not hilo_id:
            raise FilePolicyError(
                "Si se especifica mensaje_id, también se debe especificar hilo_id",
                "HILO_ID_REQUIRED_WITH_MESSAGE"
            )


class IdempotencyValidator:
    """Validador de idempotencia por mensaje y hash."""
    
    @staticmethod
    def should_use_existing_file(
        mensaje_id: Optional[UUID],
        file_hash: str,
        existing_file_hash: Optional[str]
    ) -> bool:
        """
        Determina si se debe usar un archivo existente basado en idempotencia.
        
        La idempotencia se aplica cuando:
        1. Se especifica un mensaje_id
        2. El hash del archivo nuevo coincide con uno existente para ese mensaje
        """
        return (
            mensaje_id is not None and
            existing_file_hash is not None and
            file_hash == existing_file_hash
        )