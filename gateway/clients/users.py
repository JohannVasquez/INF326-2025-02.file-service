"""Cliente para el servicio de Usuarios (Grupo 1)"""
from clients.base import BaseClient
from config import settings

class UsersClient(BaseClient):
    def __init__(self):
        super().__init__(settings.users_service_url)
    
    async def get_current_user(self):
        """Obtener información del usuario actual (requiere token)"""
        return await self.get("/v1/users/me")
    
    async def get_user(self, user_id: str):
        """Obtener un usuario por ID"""
        return await self.get(f"/v1/users/{user_id}")
    
    async def get_user_by_username(self, username: str):
        """Obtener un usuario por username"""
        return await self.get(f"/v1/users/username/{username}")
    
    async def create_user(self, username: str, email: str, password: str, full_name: str = None):
        """Crear un nuevo usuario"""
        data = {
            "username": username,
            "email": email,
            "password": password
        }
        if full_name:
            data["full_name"] = full_name
        return await self.post("/v1/users/register", json=data)
    
    async def update_user(self, user_id: str, email: str = None, full_name: str = None, is_active: bool = None):
        """Actualizar un usuario"""
        data = {}
        if email is not None:
            data["email"] = email
        if full_name is not None:
            data["full_name"] = full_name
        if is_active is not None:
            data["is_active"] = is_active
        return await self.put(f"/v1/users/{user_id}", json=data)
    
    async def delete_user(self, user_id: str):
        """Eliminar un usuario"""
        return await self.delete(f"/v1/users/{user_id}")
    
    async def authenticate(self, username_or_email: str, password: str):
        """Autenticar usuario"""
        data = {
            "username_or_email": username_or_email,
            "password": password
        }
        return await self.post("/v1/auth/login", json=data)
    
    async def get_health(self):
        """Health check del servicio de usuarios"""
        return await self.get("/health")

# Singleton
users_client = UsersClient()
