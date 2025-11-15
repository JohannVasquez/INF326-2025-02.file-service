"""Cliente base para comunicación con microservicios"""
import httpx
from typing import Optional, Dict, Any
from config import settings

class BaseClient:
    """Cliente HTTP base para todos los microservicios"""
    
    def __init__(self, base_url: str, timeout: int = None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout or settings.http_timeout
        self.client = httpx.AsyncClient(timeout=self.timeout)
    
    async def get(self, path: str, params: Optional[Dict] = None, headers: Optional[Dict] = None):
        """GET request"""
        url = f"{self.base_url}{path}"
        try:
            response = await self.client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": str(e), "status_code": e.response.status_code}
        except Exception as e:
            return {"error": str(e), "status_code": 500}
    
    async def post(self, path: str, json: Optional[Dict] = None, data: Optional[Dict] = None, 
                   files: Optional[Dict] = None, headers: Optional[Dict] = None):
        """POST request"""
        url = f"{self.base_url}{path}"
        try:
            response = await self.client.post(url, json=json, data=data, files=files, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": str(e), "status_code": e.response.status_code}
        except Exception as e:
            return {"error": str(e), "status_code": 500}
    
    async def put(self, path: str, json: Optional[Dict] = None, headers: Optional[Dict] = None):
        """PUT request"""
        url = f"{self.base_url}{path}"
        try:
            response = await self.client.put(url, json=json, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": str(e), "status_code": e.response.status_code}
        except Exception as e:
            return {"error": str(e), "status_code": 500}
    
    async def delete(self, path: str, headers: Optional[Dict] = None):
        """DELETE request"""
        url = f"{self.base_url}{path}"
        try:
            response = await self.client.delete(url, headers=headers)
            response.raise_for_status()
            return response.json() if response.text else {"success": True}
        except httpx.HTTPStatusError as e:
            return {"error": str(e), "status_code": e.response.status_code}
        except Exception as e:
            return {"error": str(e), "status_code": 500}
    
    async def close(self):
        """Cerrar conexión"""
        await self.client.aclose()
