"""Cliente para el Servicio de Archivos (Grupo 7 - Nuestro)"""
from clients.base import BaseClient
from config import settings
from typing import Optional

class FilesClient(BaseClient):
    """Cliente para interactuar con el servicio de archivos"""
    
    def __init__(self):
        super().__init__(settings.files_service_url)
    
    async def upload_file(self, file_data: bytes, filename: str, message_id: Optional[str] = None, thread_id: Optional[str] = None):
        """Subir un archivo"""
        files = {"upload": (filename, file_data)}
        data = {}
        if message_id:
            data["message_id"] = message_id
        if thread_id:
            data["thread_id"] = thread_id
        return await self.post("/v1/files", files=files, data=data)
    
    async def list_files(self, message_id: Optional[str] = None, thread_id: Optional[str] = None):
        """Listar archivos por mensaje o thread"""
        params = {}
        if message_id:
            params["message_id"] = message_id
        if thread_id:
            params["thread_id"] = thread_id
        return await self.get("/v1/files", params=params)
    
    async def get_file(self, file_id: str):
        """Obtener información de un archivo"""
        return await self.get(f"/v1/files/{file_id}")
    
    async def delete_file(self, file_id: str):
        """Eliminar un archivo"""
        return await self.delete(f"/v1/files/{file_id}")
    
    async def get_download_url(self, file_id: str):
        """Obtener URL de descarga pre-firmada"""
        return await self.post(f"/v1/files/{file_id}/presign-download")

# Instancia global
files_client = FilesClient()
