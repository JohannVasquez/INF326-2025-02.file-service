"""
Router para Servicio de Moderación (Grupo 6)
Detecta lenguaje inapropiado y gestiona moderación
"""
from fastapi import APIRouter
from typing import List
from pydantic import BaseModel
from ..client import client
from ..config import settings


router = APIRouter(prefix="/api/moderation", tags=["Moderación"])


class ModerationReport(BaseModel):
    id: str
    message_id: str
    reason: str
    severity: str  # "low", "medium", "high"
    action_taken: str  # "warning", "deleted", "user_blocked"
    reported_by: str
    created_at: str


@router.post("/check")
async def check_content(content: str, token: str):
    """
    Verifica si un contenido es apropiado
    """
    url = f"{settings.moderation_service_url}/v1/moderation/check"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.post(url, json={"content": content}, headers=headers)


@router.post("/report")
async def report_message(message_id: str, reason: str, token: str):
    """
    Reporta un mensaje inapropiado
    """
    url = f"{settings.moderation_service_url}/v1/moderation/report"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"message_id": message_id, "reason": reason}
    return await client.post(url, json=data, headers=headers)


@router.get("/reports", response_model=List[ModerationReport])
async def get_reports(token: str, skip: int = 0, limit: int = 50):
    """
    Obtiene reportes de moderación (admin only)
    """
    url = f"{settings.moderation_service_url}/v1/moderation/reports"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"skip": skip, "limit": limit}
    return await client.get(url, headers=headers, params=params)


@router.post("/reports/{report_id}/action")
async def take_moderation_action(
    report_id: str,
    action: str,  # "dismiss", "warn", "delete_message", "block_user"
    token: str
):
    """
    Toma acción sobre un reporte de moderación (admin only)
    """
    url = f"{settings.moderation_service_url}/v1/moderation/reports/{report_id}/action"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.post(url, json={"action": action}, headers=headers)
