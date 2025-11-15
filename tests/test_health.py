import pytest


@pytest.mark.asyncio
async def test_health_ok(client):
    resp = await client.get("/healthz")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "ok"
    assert "service" in data and "env" in data


@pytest.mark.asyncio
async def test_health_structure(client):
    resp = await client.get("/healthz")
    j = resp.json()
    assert set(j.keys()) == {"status", "service", "env"}