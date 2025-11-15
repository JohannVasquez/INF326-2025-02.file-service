"""
Cliente HTTP para comunicación con microservicios
Maneja reintentos, timeouts y errores comunes
"""
import httpx
from typing import Optional, Dict, Any
from fastapi import HTTPException
from .config import settings


class MicroserviceClient:
    """Cliente para comunicarse con microservicios"""
    
    def __init__(self):
        self.timeout = settings.request_timeout
        self.max_retries = settings.max_retries
    
    async def _make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """Realiza request HTTP con manejo de errores"""
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json,
                    data=data,
                    files=files,
                    params=params,
                )
                
                # Si el servicio responde con error, propagarlo
                if response.status_code >= 400:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=response.json() if response.text else "Service error"
                    )
                
                return response
                
            except httpx.TimeoutException:
                raise HTTPException(
                    status_code=504,
                    detail="Service timeout - el microservicio no respondió a tiempo"
                )
            except httpx.ConnectError:
                raise HTTPException(
                    status_code=503,
                    detail="Service unavailable - no se pudo conectar al microservicio"
                )
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error interno: {str(e)}"
                )
    
    async def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """GET request"""
        response = await self._make_request("GET", url, **kwargs)
        return response.json()
    
    async def post(self, url: str, **kwargs) -> Dict[str, Any]:
        """POST request"""
        response = await self._make_request("POST", url, **kwargs)
        return response.json()
    
    async def put(self, url: str, **kwargs) -> Dict[str, Any]:
        """PUT request"""
        response = await self._make_request("PUT", url, **kwargs)
        return response.json()
    
    async def delete(self, url: str, **kwargs) -> Dict[str, Any]:
        """DELETE request"""
        response = await self._make_request("DELETE", url, **kwargs)
        return response.json()


# Instancia global del cliente
client = MicroserviceClient()
