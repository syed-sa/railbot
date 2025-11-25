# app/api/chat.py

from fastapi import APIRouter
from pydantic import BaseModel
from app.services.chat_service import ChatService

router = APIRouter()
chat_service = ChatService()


class ChatRequest(BaseModel):
    conversation_id: str
    message: str


@router.post("/")
def chat_endpoint(payload: ChatRequest):
    reply = chat_service.process_user_message(
        conversation_id=payload.conversation_id,
        user_text=payload.message
    )
    return {"reply": reply}
