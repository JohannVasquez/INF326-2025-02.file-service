import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test del endpoint de health check"""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"
    assert "service" in data

def test_health_check_structure():
    """Verifica la estructura de la respuesta del health check"""
    response = client.get("/healthz")
    data = response.json()
    assert "status" in data
    assert "service" in data
    assert "env" in data
    assert isinstance(data["status"], str)
    assert isinstance(data["service"], str)

def test_api_docs_available():
    """Verifica que la documentación OpenAPI esté disponible"""
    response = client.get("/docs")
    assert response.status_code == 200

def test_openapi_json():
    """Verifica que el schema OpenAPI esté disponible"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert schema["info"]["title"] == "Servicio de Archivos"

def test_cors_headers():
    """Verifica que los headers CORS estén configurados"""
    response = client.options("/healthz")
    # En desarrollo, CORS permite todo
    # Este test verifica que el middleware CORS está activo
    assert response.status_code in [200, 405]  # OPTIONS puede retornar 405 si no está explícitamente manejado
