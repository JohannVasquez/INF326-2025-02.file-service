"""
Seguridad y autenticación JWT para el servicio de archivos.
"""

from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.core.config import settings
from app.domain.models import UserInfo


# Esquema de autenticación Bearer
security = HTTPBearer()


class AuthenticationError(Exception):
    """Error de autenticación."""
    
    def __init__(self, message: str, status_code: int = status.HTTP_401_UNAUTHORIZED):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthorizationError(Exception):
    """Error de autorización."""
    
    def __init__(self, message: str, status_code: int = status.HTTP_403_FORBIDDEN):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class JWTValidator:
    """Validador de tokens JWT."""
    
    def __init__(self, public_key_pem: str, algorithm: str = "RS256"):
        self.public_key_pem = public_key_pem
        self.algorithm = algorithm
        
        if not self.public_key_pem:
            raise ValueError("JWT public key PEM is required")
    
    def validate_token(self, token: str) -> dict:
        """
        Valida un token JWT y retorna el payload.
        
        Args:
            token: Token JWT a validar
            
        Returns:
            dict: Payload del token
            
        Raises:
            AuthenticationError: Si el token es inválido
        """
        try:
            payload = jwt.decode(
                token, 
                self.public_key_pem, 
                algorithms=[self.algorithm]
            )
            
            # Validar que tenga los campos requeridos
            if "sub" not in payload:
                raise AuthenticationError("Token inválido: campo 'sub' requerido")
            
            return payload
            
        except JWTError as e:
            raise AuthenticationError(f"Token JWT inválido: {str(e)}")
    
    def extract_user_info(self, payload: dict) -> UserInfo:
        """
        Extrae información del usuario desde el payload del JWT.
        
        Args:
            payload: Payload decodificado del JWT
            
        Returns:
            UserInfo: Información del usuario
            
        Raises:
            AuthenticationError: Si el payload no tiene el formato esperado
        """
        try:
            user_id_str = payload.get("sub")
            if not user_id_str:
                raise AuthenticationError("Token inválido: 'sub' vacío")
            
            # Convertir a UUID
            try:
                user_id = UUID(user_id_str)
            except ValueError:
                raise AuthenticationError("Token inválido: 'sub' no es un UUID válido")
            
            # Extraer información adicional opcional
            email = payload.get("email")
            roles = payload.get("roles", [])
            
            # Asegurar que roles sea una lista
            if not isinstance(roles, list):
                roles = []
            
            return UserInfo(
                user_id=user_id,
                email=email,
                roles=roles
            )
            
        except KeyError as e:
            raise AuthenticationError(f"Token inválido: campo requerido {e}")


# Instancia global del validador JWT
_jwt_validator: Optional[JWTValidator] = None


def get_jwt_validator() -> JWTValidator:
    """Obtiene la instancia del validador JWT."""
    global _jwt_validator
    
    if _jwt_validator is None:
        _jwt_validator = JWTValidator(
            public_key_pem=settings.jwt_public_key_pem,
            algorithm=settings.jwt_algorithm
        )
    
    return _jwt_validator


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserInfo:
    """
    Dependencia de FastAPI para obtener el usuario actual desde el JWT.
    
    Args:
        credentials: Credenciales de autorización Bearer
        
    Returns:
        UserInfo: Información del usuario autenticado
        
    Raises:
        HTTPException: Si el token es inválido o no se puede extraer la información
    """
    try:
        validator = get_jwt_validator()
        payload = validator.validate_token(credentials.credentials)
        user_info = validator.extract_user_info(payload)
        
        return user_info
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[UserInfo]:
    """
    Dependencia de FastAPI para obtener el usuario actual de forma opcional.
    
    Args:
        credentials: Credenciales de autorización Bearer (opcional)
        
    Returns:
        Optional[UserInfo]: Información del usuario si está autenticado, None si no
    """
    if not credentials:
        return None
    
    try:
        validator = get_jwt_validator()
        payload = validator.validate_token(credentials.credentials)
        user_info = validator.extract_user_info(payload)
        
        return user_info
        
    except AuthenticationError:
        # En modo opcional, no lanzamos excepción
        return None


class PermissionChecker:
    """Verificador de permisos básicos."""
    
    @staticmethod
    def can_access_canal(user: UserInfo, canal_id: UUID) -> bool:
        """
        Verifica si el usuario puede acceder a un canal.
        
        Por ahora implementamos una lógica básica.
        En un sistema real, esto consultaría el servicio de canales.
        
        Args:
            user: Información del usuario
            canal_id: ID del canal
            
        Returns:
            bool: True si puede acceder, False si no
        """
        # TODO: Implementar verificación real con el servicio de canales
        # Por ahora, permitimos acceso a todos los usuarios autenticados
        return True
    
    @staticmethod
    def can_delete_file(user: UserInfo, file_owner_id: UUID) -> bool:
        """
        Verifica si el usuario puede eliminar un archivo.
        
        Args:
            user: Información del usuario
            file_owner_id: ID del propietario del archivo
            
        Returns:
            bool: True si puede eliminar, False si no
        """
        # Un usuario puede eliminar sus propios archivos
        if user.user_id == file_owner_id:
            return True
        
        # Los moderadores pueden eliminar cualquier archivo
        if "moderator" in user.roles or "admin" in user.roles:
            return True
        
        return False


def require_permission(permission_check) -> callable:
    """
    Decorador para requerir permisos específicos.
    
    Args:
        permission_check: Función que verifica el permiso
        
    Returns:
        callable: Decorador
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extraer user desde kwargs (debe ser inyectado por FastAPI)
            user = kwargs.get("current_user")
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no autenticado"
                )
            
            # Verificar permiso
            if not permission_check(user, *args, **kwargs):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Permisos insuficientes"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator