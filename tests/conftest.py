import asyncio
import os
import sys
import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator

# Ensure repository root is on sys.path for `import app`
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from app.main import app
from app.db import Base, get_session as app_get_session


class _FakeEventBus:
    async def connect(self):
        return None

    async def publish(self, routing_key: str, payload: dict):
        return None


@pytest.fixture
async def test_db():
    """Create an isolated in-memory SQLite DB for each test and yield a sessionmaker."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def _get_session() -> AsyncGenerator[AsyncSession, None]:
        async with SessionLocal() as session:
            try:
                yield session
            finally:
                pass

    # Override FastAPI dependency
    app.dependency_overrides[app_get_session] = _get_session

    try:
        yield SessionLocal
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()


@pytest.fixture
def patch_infra(monkeypatch):
    """Patch external infrastructure: MinIO, EventBus, startup hooks."""
    # Avoid MinIO bucket creation on startup
    import app.main as app_main
    monkeypatch.setattr(app_main, "ensure_bucket", lambda: None)

    # Patch event bus in both modules where it's used
    import app.events as app_events
    import app.routers.files as files_router

    fake_bus = _FakeEventBus()
    monkeypatch.setattr(app_events, "event_bus", fake_bus)
    monkeypatch.setattr(files_router, "event_bus", fake_bus)

    # Patch storage operations used by routers
    def _fake_put_object(object_key: str, data, length: int, content_type: str):
        # Return deterministic bucket and the provided key
        return ("test-bucket", object_key)

    def _fake_presign_get(object_key: str, expires_seconds: int = 3600) -> str:
        return f"https://public.example.com/{object_key}?exp={expires_seconds}"

    monkeypatch.setattr(files_router, "put_object", _fake_put_object)
    monkeypatch.setattr(files_router, "presign_get", _fake_presign_get)


@pytest.fixture
async def client(test_db, patch_infra):
    """HTTPX AsyncClient bound to FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
