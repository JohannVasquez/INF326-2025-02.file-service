"""
Router para Servicio de Usuarios (Grupo 1)
Registro, autenticación y perfil básico
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from ..client import client
from ..config import settings


router = APIRouter(prefix="/api/users", tags=["Usuarios"])


# Modelos de ejemplo
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserProfile(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: str


@router.post("/register", response_model=UserProfile)
async def register_user(user: UserRegister):
    """
    Registra un nuevo usuario
    """
    url = f"{settings.users_service_url}/v1/users"
    return await client.post(url, json=user.dict())


@router.post("/login")
async def login_user(credentials: UserLogin):
    """
    Autentica un usuario y devuelve token JWT
    """
    url = f"{settings.users_service_url}/v1/auth/login"
    return await client.post(url, json=credentials.dict())


@router.get("/me", response_model=UserProfile)
async def get_current_user(token: str):
    """
    Obtiene perfil del usuario actual
    Requiere token JWT en header Authorization
    """
    url = f"{settings.users_service_url}/v1/users/me"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.get(url, headers=headers)


@router.get("/{user_id}", response_model=UserProfile)
async def get_user_by_id(user_id: str):
    """
    Obtiene perfil de usuario por ID
    """
    url = f"{settings.users_service_url}/v1/users/{user_id}"
    return await client.get(url)


@router.put("/me")
async def update_user_profile(user_data: dict, token: str):
    """
    Actualiza perfil del usuario actual
    """
    url = f"{settings.users_service_url}/v1/users/me"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.put(url, json=user_data, headers=headers)


@router.get("/")
async def list_users(skip: int = 0, limit: int = 50):
    """
    Lista usuarios registrados
    """
    url = f"{settings.users_service_url}/v1/users"
    params = {"skip": skip, "limit": limit}
    return await client.get(url, params=params)
