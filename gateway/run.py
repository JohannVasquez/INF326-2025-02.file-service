"""
Script de entrada para el API Gateway
"""
import uvicorn
from app.main import app
from app.config import settings


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.gateway_host,
        port=settings.gateway_port,
        reload=True,  # Solo en desarrollo
        log_level="info"
    )
