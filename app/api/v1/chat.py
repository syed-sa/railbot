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
async def chat(request: ChatRequest):
    # Call the async method directly with await
    reply = await chat_service.process_user_message(
        request.conversation_id, 
        request.message
    )
    return {"reply": reply}
