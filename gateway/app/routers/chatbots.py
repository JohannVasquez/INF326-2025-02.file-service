"""
Router para Chatbots (Grupos 9-13)
Agrupa todos los servicios de chatbots
"""
from fastapi import APIRouter
from typing import Optional
from pydantic import BaseModel
from ..client import client
from ..config import settings


router = APIRouter(prefix="/api/chatbot", tags=["Chatbots"])


class ChatbotQuery(BaseModel):
    query: str
    context: Optional[dict] = None


class ChatbotResponse(BaseModel):
    response: str
    source: str  # "academic", "utility", "calc", "wiki", "programming"
    confidence: Optional[float] = None


# Chatbot Académico (Grupo 9)
@router.post("/academic", response_model=ChatbotResponse)
async def query_academic_chatbot(query: ChatbotQuery, token: str):
    """
    Consulta al chatbot académico
    Ejemplo: "¿Cuándo es la próxima prueba?"
    """
    url = f"{settings.chatbot_academic_service_url}/v1/chatbot/query"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.post(url, json=query.dict(), headers=headers)


# Chatbot de Utilidad (Grupo 10)
@router.post("/utility", response_model=ChatbotResponse)
async def query_utility_chatbot(query: ChatbotQuery, token: str):
    """
    Chatbot de utilidad: recordatorios, encuestas, etc.
    Ejemplo: "Recordar reunión mañana a las 3pm"
    """
    url = f"{settings.chatbot_utility_service_url}/v1/chatbot/query"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.post(url, json=query.dict(), headers=headers)


@router.post("/utility/reminder")
async def create_reminder(
    message: str,
    datetime: str,
    channel_id: str,
    token: str
):
    """
    Crea un recordatorio
    """
    url = f"{settings.chatbot_utility_service_url}/v1/reminders"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "message": message,
        "datetime": datetime,
        "channel_id": channel_id
    }
    return await client.post(url, json=data, headers=headers)


# Chatbot de Cálculo (Grupo 11)
@router.post("/calc", response_model=ChatbotResponse)
async def query_calc_chatbot(expression: str, token: str):
    """
    Resuelve expresiones matemáticas
    Ejemplo: "integral de x^2", "derivada de sen(x)"
    """
    url = f"{settings.chatbot_calc_service_url}/v1/calculate"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.post(url, json={"expression": expression}, headers=headers)


# Chatbot de Wikipedia (Grupo 12)
@router.post("/wiki", response_model=ChatbotResponse)
async def query_wiki_chatbot(topic: str, token: str):
    """
    Consulta información de Wikipedia
    Ejemplo: "¿Qué es la inteligencia artificial?"
    """
    url = f"{settings.chatbot_wiki_service_url}/v1/wiki/query"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.post(url, json={"topic": topic}, headers=headers)


# Chatbot de Programación (Grupo 13)
@router.post("/programming", response_model=ChatbotResponse)
async def query_programming_chatbot(query: ChatbotQuery, token: str):
    """
    Resuelve dudas de programación
    Ejemplo: "¿Cómo ordenar una lista en Python?"
    """
    url = f"{settings.chatbot_programming_service_url}/v1/chatbot/query"
    headers = {"Authorization": f"Bearer {token}"}
    return await client.post(url, json=query.dict(), headers=headers)


@router.post("/programming/explain")
async def explain_code(code: str, language: str, token: str):
    """
    Explica un fragmento de código
    """
    url = f"{settings.chatbot_programming_service_url}/v1/explain"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"code": code, "language": language}
    return await client.post(url, json=data, headers=headers)
