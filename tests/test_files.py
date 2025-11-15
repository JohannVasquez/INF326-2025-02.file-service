import io
import uuid
import pytest


async def _create_file(client, message_id: str = "msg-1"):
    files = {"upload": ("hello.txt", b"hello world", "text/plain")}
    params = {"message_id": message_id}
    r = await client.post("/v1/files", files=files, params=params)
    assert r.status_code == 201, r.text
    return r.json()


@pytest.mark.asyncio
async def test_upload_file_success(client):
    data = await _create_file(client, message_id="m-123")
    assert data["filename"] == "hello.txt"
    assert data["mime_type"] == "text/plain"
    assert data["message_id"] == "m-123"
    # bucket and object_key come from patched storage
    assert data["bucket"] == "test-bucket"
    assert isinstance(data["object_key"], str)


@pytest.mark.asyncio
async def test_upload_file_missing_association(client):
    files = {"upload": ("hello.txt", b"hello world", "text/plain")}
    r = await client.post("/v1/files", files=files)
    assert r.status_code == 400
    body = r.json()
    assert body["detail"]["code"] == "MISSING_ASSOCIATION"


@pytest.mark.asyncio
async def test_get_file_found(client):
    created = await _create_file(client, message_id="m-get")
    file_id = created["id"]
    r = await client.get(f"/v1/files/{file_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == file_id
    assert data["filename"] == "hello.txt"


@pytest.mark.asyncio
async def test_get_file_not_found(client):
    fake_id = str(uuid.uuid4())
    r = await client.get(f"/v1/files/{fake_id}")
    assert r.status_code == 404
    assert r.json()["detail"]["code"] == "FILE_NOT_FOUND"


@pytest.mark.asyncio
async def test_list_files_by_message_id(client):
    created = await _create_file(client, message_id="m-list-1")
    r = await client.get("/v1/files", params={"message_id": "m-list-1"})
    assert r.status_code == 200
    arr = r.json()
    assert isinstance(arr, list) and len(arr) >= 1
    assert any(item["id"] == created["id"] for item in arr)


@pytest.mark.asyncio
async def test_list_files_missing_filter(client):
    r = await client.get("/v1/files")
    assert r.status_code == 400
    assert r.json()["detail"]["code"] == "MISSING_FILTER"


@pytest.mark.asyncio
async def test_delete_file_success(client):
    created = await _create_file(client, message_id="m-del")
    file_id = created["id"]
    r = await client.delete(f"/v1/files/{file_id}")
    assert r.status_code == 204

    # Verify it is not retrievable anymore
    r2 = await client.get(f"/v1/files/{file_id}")
    assert r2.status_code == 404


@pytest.mark.asyncio
async def test_delete_file_not_found(client):
    r = await client.delete(f"/v1/files/{uuid.uuid4()}")
    assert r.status_code == 404
    assert r.json()["detail"]["code"] == "FILE_NOT_FOUND"


@pytest.mark.asyncio
async def test_presign_download_success(client):
    created = await _create_file(client, message_id="m-dl")
    file_id = created["id"]
    r = await client.post(f"/v1/files/{file_id}/presign-download")
    assert r.status_code == 200
    body = r.json()
    assert "url" in body and body["url"].startswith("https://public.example.com/")
    assert body["expires_in"] == 3600


@pytest.mark.asyncio
async def test_presign_download_not_found(client):
    r = await client.post(f"/v1/files/{uuid.uuid4()}/presign-download")
    assert r.status_code == 404
    assert r.json()["detail"]["code"] == "FILE_NOT_FOUND"
