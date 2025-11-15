"""Router para Moderación"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from clients.moderation import moderation_client

router = APIRouter()

class MessageCheck(BaseModel):
    user_id: str
    channel_id: str
    content: str

class TextAnalysis(BaseModel):
    text: str

class BlacklistWord(BaseModel):
    word: str

@router.post("/check")
async def check_message(data: MessageCheck):
    """Moderar un mensaje"""
    result = await moderation_client.check_message(
        data.user_id,
        data.channel_id,
        data.content
    )
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result

@router.post("/analyze")
async def analyze_text(data: TextAnalysis):
    """Analizar texto"""
    result = await moderation_client.analyze_text(data.text)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result

@router.get("/status/{user_id}/{channel_id}")
async def get_user_status(user_id: str, channel_id: str):
    """Obtener estado de moderación de un usuario"""
    result = await moderation_client.get_user_status(user_id, channel_id)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result

@router.get("/banned-users")
async def list_banned_users():
    """Listar usuarios baneados"""
    result = await moderation_client.list_banned_users()
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result

@router.get("/blacklist/words")
async def list_blacklist_words():
    """Listar palabras de lista negra"""
    result = await moderation_client.list_blacklist_words()
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result

@router.post("/blacklist/words")
async def add_blacklist_word(data: BlacklistWord):
    """Agregar palabra a lista negra"""
    result = await moderation_client.add_blacklist_word(data.word)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result
