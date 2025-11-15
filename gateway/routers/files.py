"""Router para Archivos"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from typing import Optional
from clients.files import files_client

router = APIRouter()

@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    message_id: Optional[str] = Form(None),
    thread_id: Optional[str] = Form(None)
):
    """Subir un archivo"""
    file_data = await file.read()
    result = await files_client.upload_file(
        file_data,
        file.filename,
        message_id,
        thread_id
    )
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result

@router.get("")
async def list_files(
    message_id: Optional[str] = Query(None),
    thread_id: Optional[str] = Query(None)
):
    """Listar archivos por mensaje o thread - Requiere al menos uno de los filtros"""
    if not message_id and not thread_id:
        raise HTTPException(
            status_code=400, 
            detail={"code": "MISSING_FILTER", "message": "Debe proporcionar message_id o thread_id como filtro"}
        )
    result = await files_client.list_files(message_id, thread_id)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result

@router.get("/{file_id}")
async def get_file(file_id: str):
    """Obtener información de un archivo"""
    result = await files_client.get_file(file_id)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 404), detail=result)
    return result

@router.delete("/{file_id}")
async def delete_file(file_id: str):
    """Eliminar un archivo"""
    result = await files_client.delete_file(file_id)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result

@router.post("/{file_id}/download-url")
async def get_download_url(file_id: str):
    """Obtener URL de descarga"""
    result = await files_client.get_download_url(file_id)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result
