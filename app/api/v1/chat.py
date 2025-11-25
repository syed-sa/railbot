# app/api/chat.py
from fastapi import APIRouter
from fastapi.params import Depends
from app.models.chat import ChatRequest
from app.services.chat_service import ChatService

router = APIRouter()
def get_chat_service() -> ChatService:
    return ChatService()





@router.post("/")
async def chat(request: ChatRequest,chat_service: ChatService = Depends(get_chat_service)):
    # Call the async method directly with await
    reply = await chat_service.process_user_message(
        request.conversation_id, 
        request.message
    )
    return {"reply": reply}
