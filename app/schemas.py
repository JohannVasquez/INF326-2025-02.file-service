from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime

class FileOut(BaseModel):
    id: UUID
    filename: str
    mime_type: str
    size: int
    bucket: str
    object_key: str
    message_id: Optional[str] = None
    thread_id: Optional[str] = None
    checksum_sha256: str
    created_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ErrorResponse(BaseModel):
    error: dict
