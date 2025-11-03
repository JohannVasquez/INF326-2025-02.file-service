# Tests para el Servicio de Archivos

Este directorio contiene los tests automatizados del proyecto.

## Ejecutar tests

### Localmente

```powershell
# Instalar dependencias de testing
pip install pytest pytest-asyncio httpx

# Ejecutar todos los tests
pytest -v

# Ejecutar con cobertura
pytest --cov=app --cov-report=html

# Ejecutar un test específico
pytest tests/test_api.py::test_health_check -v
```

### En Docker

```powershell
docker compose exec api pytest -v
```

## Estructura

- `test_api.py` - Tests de endpoints básicos
- `conftest.py` - Configuración compartida de pytest

## Agregar más tests

Para agregar tests:
1. Crea un archivo `test_*.py`
2. Define funciones que empiecen con `test_`
3. Usa `pytest` como framework

Ejemplo:

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_mi_endpoint():
    response = client.get("/mi-endpoint")
    assert response.status_code == 200
```

## CI/CD

Los tests se ejecutan automáticamente en el pipeline de GitHub Actions antes de cada despliegue.
