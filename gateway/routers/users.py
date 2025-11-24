"""Router para Usuarios"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from clients.users import users_client

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None

class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserLogin(BaseModel):
    username_or_email: str
    password: str

@router.get("/me")
async def get_current_user():
    """Obtener información del usuario actual (requiere autenticación)"""
    result = await users_client.get_current_user()
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result

@router.get("/{user_id}")
async def get_user(user_id: str):
    """Obtener un usuario por ID"""
    result = await users_client.get_user(user_id)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 404), detail=result)
    return result

@router.get("/username/{username}")
async def get_user_by_username(username: str):
    """Obtener un usuario por username"""
    result = await users_client.get_user_by_username(username)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 404), detail=result)
    return result

@router.post("")
async def create_user(user: UserCreate):
    """Crear un nuevo usuario"""
    result = await users_client.create_user(
        user.username,
        user.email,
        user.password,
        user.full_name
    )
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result

@router.put("/{user_id}")
async def update_user(user_id: str, user: UserUpdate):
    """Actualizar un usuario"""
    result = await users_client.update_user(
        user_id,
        user.email,
        user.full_name,
        user.is_active
    )
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result

@router.delete("/{user_id}")
async def delete_user(user_id: str):
    """Eliminar un usuario"""
    result = await users_client.delete_user(user_id)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result

@router.post("/auth/login")
async def login(credentials: UserLogin):
    """Autenticar usuario"""
    result = await users_client.authenticate(
        credentials.username_or_email,
        credentials.password
    )
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 401), detail=result)
    return result

@router.get("/health")
async def health_check():
    """Health check del servicio de usuarios"""
    result = await users_client.get_health()
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result
