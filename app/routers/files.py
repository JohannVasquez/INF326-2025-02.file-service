from fastapi import APIRouter, UploadFile, File as FFile, Depends, HTTPException, Query
from fastapi import status
from typing import Optional, List
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timezone
from io import BytesIO

from ..db import get_session
from ..models import File as FileModel
from ..schemas import FileOut
from ..storage import put_object, presign_get
from ..events import event_bus
from ..utils import sha256_bytesio

router = APIRouter(prefix="/v1/files", tags=["files"])

@router.post("", response_model=FileOut, status_code=status.HTTP_201_CREATED)
async def upload_file(
    upload: UploadFile = FFile(...),
    message_id: Optional[str] = None,
    thread_id: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    if not message_id and not thread_id:
        raise HTTPException(status_code=400, detail={"code":"MISSING_ASSOCIATION","message":"Debe enviar message_id o thread_id"})

    # Read into memory to hash and upload (for demo; en producción, stream/chunk)
    raw = await upload.read()
    bio = BytesIO(raw)
    checksum, total = sha256_bytesio(BytesIO(raw))

    object_key = f"{uuid4()}/{upload.filename}"
    bucket, key = put_object(object_key, BytesIO(raw), length=len(raw), content_type=upload.content_type or "application/octet-stream")

    file_row = FileModel(
        filename=upload.filename,
        mime_type=upload.content_type or "application/octet-stream",
        size=total,
        bucket=bucket,
        object_key=key,
        message_id=message_id,
        thread_id=thread_id,
        checksum_sha256=checksum,
    )
    session.add(file_row)
    await session.commit()
    await session.refresh(file_row)

    # Emit event
    await event_bus.publish(
        routing_key="files.added.v1",
        payload={
            "type":"files.added.v1",
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "data": {
                "file_id": str(file_row.id),
                "bucket": file_row.bucket,
                "object_key": file_row.object_key,
                "mime_type": file_row.mime_type,
                "size": file_row.size,
                "message_id": file_row.message_id,
                "thread_id": file_row.thread_id,
                "checksum_sha256": file_row.checksum_sha256
            }
        }
    )

    return file_row

@router.get("/{file_id}", response_model=FileOut)
async def get_file(file_id: UUID, session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(FileModel).where(FileModel.id==file_id, FileModel.deleted_at.is_(None)))
    file = res.scalar_one_or_none()
    if not file:
        raise HTTPException(status_code=404, detail={"code":"FILE_NOT_FOUND","message":"No existe el archivo"})
    return file

@router.get("", response_model=List[FileOut])
async def list_files(
    message_id: Optional[str] = Query(None),
    thread_id: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session)
):
    if not message_id and not thread_id:
        raise HTTPException(status_code=400, detail={"code":"MISSING_FILTER","message":"Debe filtrar por message_id o thread_id"})
    stmt = select(FileModel).where(FileModel.deleted_at.is_(None))
    if message_id:
        stmt = stmt.where(FileModel.message_id==message_id)
    if thread_id:
        stmt = stmt.where(FileModel.thread_id==thread_id)
    res = await session.execute(stmt.order_by(FileModel.created_at.desc()))
    return res.scalars().all()

@router.delete("/{file_id}", status_code=204)
async def delete_file(file_id: UUID, session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(FileModel).where(FileModel.id==file_id, FileModel.deleted_at.is_(None)))
    file = res.scalar_one_or_none()
    if not file:
        raise HTTPException(status_code=404, detail={"code":"FILE_NOT_FOUND","message":"No existe el archivo"})
    file.deleted_at = datetime.now(timezone.utc)
    await session.commit()

    await event_bus.publish(
        routing_key="files.deleted.v1",
        payload={
            "type":"files.deleted.v1",
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "data": {
                "file_id": str(file.id),
                "bucket": file.bucket,
                "object_key": file.object_key
            }
        }
    )
    return

@router.post("/{file_id}/presign-download")
async def presign_download(file_id: UUID, session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(FileModel).where(FileModel.id==file_id, FileModel.deleted_at.is_(None)))
    file = res.scalar_one_or_none()
    if not file:
        raise HTTPException(status_code=404, detail={"code":"FILE_NOT_FOUND","message":"No existe el archivo"})
    url = presign_get(file.object_key, 3600)
    return {"url": url, "expires_in": 3600}
