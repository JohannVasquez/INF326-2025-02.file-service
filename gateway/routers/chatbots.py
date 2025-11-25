"""Router para chatbots de soporte"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from clients.chatbots import wikipedia_chat_client, programming_chat_client

router = APIRouter()


class ChatPrompt(BaseModel):
    message: str


@router.post("/wiki")
async def ask_wikipedia(prompt: ChatPrompt):
    result = await wikipedia_chat_client.ask(prompt.message)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result


@router.post("/programming")
async def ask_programming_bot(prompt: ChatPrompt):
    result = await programming_chat_client.ask(prompt.message)
    if "error" in result:
        raise HTTPException(status_code=result.get("status_code", 500), detail=result)
    return result
