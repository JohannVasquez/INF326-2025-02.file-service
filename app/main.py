import os
import uuid
import json
import sqlite3
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException, status
from fastapi.responses import FileResponse

import httpx

app = FastAPI(title="File Service - Microservicio de archivos")

DB_PATH = os.getenv("FILE_SERVICE_DB", "filemeta.db")
STORAGE_DIR = os.getenv("FILE_SERVICE_STORAGE", "storage")
EVENT_HOOKS = os.getenv("FILE_SERVICE_EVENT_HOOKS", "")


def init_storage():
    os.makedirs(STORAGE_DIR, exist_ok=True)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS files (
                id TEXT PRIMARY KEY,
                original_name TEXT,
                path TEXT,
                content_type TEXT,
                size INTEGER,
                chat_id TEXT,
                message_id TEXT,
                thread_id TEXT,
                created_at TEXT
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


@app.on_event("startup")
def startup():
    init_storage()
    init_db()


def save_metadata(meta: dict):
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT INTO files (id, original_name, path, content_type, size, chat_id, message_id, thread_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                meta["id"],
                meta["original_name"],
                meta["path"],
                meta.get("content_type"),
                meta.get("size"),
                meta.get("chat_id"),
                meta.get("message_id"),
                meta.get("thread_id"),
                meta.get("created_at"),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def get_metadata(file_id: str) -> Optional[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute("SELECT * FROM files WHERE id = ?", (file_id,))
        row = cur.fetchone()
        if not row:
            return None
        return dict(row)
    finally:
        conn.close()


def delete_metadata(file_id: str):
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("DELETE FROM files WHERE id = ?", (file_id,))
        conn.commit()
    finally:
        conn.close()


async def dispatch_event(event: dict):
    """Try to POST the event to configured webhook(s). If none are configured, append to local events.log."""
    hooks = [h.strip() for h in EVENT_HOOKS.split(",") if h.strip()]
    if not hooks:
        # fallback: append to local log
        with open("events.log", "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
        return

    async with httpx.AsyncClient(timeout=5.0) as client:
        for url in hooks:
            try:
                await client.post(url, json=event)
            except Exception as e:
                # if webhook fails, record locally
                with open("events.log", "a", encoding="utf-8") as f:
                    f.write(json.dumps({"error": str(e), "url": url, "event": event}, ensure_ascii=False) + "\n")


@app.post("/internal-upload")
async def internal_upload(background_tasks: BackgroundTasks):
    """Read a local test file and POST it to the /upload endpoint internally.

    Returns the same JSON response the /upload endpoint returns.
    Useful to trigger uploads from inside the container and see logs.
    """
    test_path = os.path.join(os.path.dirname(__file__), "test_upload_from_main.txt")
    if not os.path.exists(test_path):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Test file not found")

    url = f"http://127.0.0.1:8000/upload"
    # post multipart file
    async with httpx.AsyncClient() as client:
        with open(test_path, "rb") as f:
            files = {"file": ("test_upload_from_main.txt", f, "text/plain")}
            data = {"chat_id": "internal-test", "message_id": "internal"}
            try:
                resp = await client.post(url, data=data, files=files, timeout=30.0)
            except httpx.RequestError as exc:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal request failed: {exc}")

    try:
        return resp.json()
    except Exception:
        return {"status_code": resp.status_code, "text": resp.text}


@app.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    chat_id: str = Form(...),
    message_id: Optional[str] = Form(None),
    thread_id: Optional[str] = Form(None),
):
    """Upload a file and associate it to a chat/message/thread.

    Required form fields: file, chat_id
    Optional: message_id, thread_id
    """
    file_id = str(uuid.uuid4())
    filename = file.filename or "unnamed"
    dest_path = os.path.join(STORAGE_DIR, file_id)

    # save file to disk
    size = 0
    try:
        with open(dest_path, "wb") as out:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)
                size += len(chunk)
    finally:
        await file.close()

    meta = {
        "id": file_id,
        "original_name": filename,
        "path": dest_path,
        "content_type": file.content_type,
        "size": size,
        "chat_id": chat_id,
        "message_id": message_id,
        "thread_id": thread_id,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }

    save_metadata(meta)

    event = {"type": "archivo_agregado", "file": meta}
    background_tasks.add_task(dispatch_event, event)

    return {"status": "ok", "file_id": file_id, "download_url": f"/files/{file_id}"}


@app.get("/files/{file_id}")
def download_file(file_id: str):
    meta = get_metadata(file_id)
    if not meta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado")

    file_path = meta["path"]
    if not os.path.exists(file_path):
        # cleanup record
        delete_metadata(file_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado en almacenamiento")

    return FileResponse(path=file_path, filename=meta.get("original_name"), media_type=meta.get("content_type") or "application/octet-stream")


@app.get("/files/{file_id}/meta")
def file_meta(file_id: str):
    meta = get_metadata(file_id)
    if not meta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metadata no encontrada")
    return meta


@app.delete("/files/{file_id}")
def delete_file(file_id: str, background_tasks: BackgroundTasks):
    meta = get_metadata(file_id)
    if not meta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado")

    file_path = meta["path"]
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al eliminar archivo: {e}")

    delete_metadata(file_id)

    event = {"type": "archivo_eliminado", "file_id": file_id, "chat_id": meta.get("chat_id"), "message_id": meta.get("message_id"), "thread_id": meta.get("thread_id"), "deleted_at": datetime.utcnow().isoformat() + "Z"}
    background_tasks.add_task(dispatch_event, event)

    return {"status": "deleted", "file_id": file_id}
