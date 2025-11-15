"""
Router para Servicio de Archivos (Grupo 7 - NUESTRO SERVICIO)
Permite subir y asociar archivos a mensajes o hilos
"""
from fastapi import APIRouter, UploadFile, File, Form
from typing import List, Optional
from pydantic import BaseModel
from ..client import client
from ..config import settings


router = APIRouter(prefix="/api/files", tags=["Archivos"])


class FileMetadata(BaseModel):
    id: str
    filename: str
    mime_type: str
    size: int
    message_id: Optional[str] = None
    thread_id: Optional[str] = None
    uploaded_by: str
    uploaded_at: str
    download_url: Optional[str] = None


@router.post("/upload", response_model=FileMetadata)
async def upload_file(
    file: UploadFile = File(...),
    message_id: Optional[str] = Form(None),
    thread_id: Optional[str] = Form(None),
    token: str = Form(...)
):
    """
    Sube un archivo y lo asocia a un mensaje o hilo
    """
    url = f"{settings.files_service_url}/v1/files"
    headers = {"Authorization": f"Bearer {token}"}
    
    files = {"file": (file.filename, file.file, file.content_type)}
    data = {}
    if message_id:
        data["message_id"] = message_id
    if thread_id:
        data["thread_id"] = thread_id
    
    return await client.post(url, files=files, data=data, headers=headers)


@router.get("/", response_model=List[FileMetadata])
async def list_files(
    token: str,
    message_id: Optional[str] = None,
    thread_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    """
    Lista archivos (filtrados por mensaje o hilo)
    """
    url = f"{settings.files_service_url}/v1/files"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"skip": skip, "limit": limit}
    if message_id:
        params["message_id"] = message_id
    if thread_id:
        params["thread_id"] = thread_id
    return await client.get(url, headers=headers, params=params)


@router.get("/{file_id}", response_model=FileMetadata)
async def get_file_metadata(file_id: str, token: str):
    """
    Obtiene metadatos de un archivo
    """
    url = f"{settings.files_service_url}/v1/files/{file_id}"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.get(url, headers=headers)


@router.post("/{file_id}/presign-download")
async def get_download_url(file_id: str, token: str):
    """
    Obtiene URL prefirmada para descargar el archivo
    """
    url = f"{settings.files_service_url}/v1/files/{file_id}/presign-download"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.post(url, headers=headers)


@router.delete("/{file_id}")
async def delete_file(file_id: str, token: str):
    """
    Elimina un archivo
    """
    url = f"{settings.files_service_url}/v1/files/{file_id}"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.delete(url, headers=headers)
