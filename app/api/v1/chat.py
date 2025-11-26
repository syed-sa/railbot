""""API endpoints for chat interactions.
"""
from fastapi import APIRouter
from fastapi.params import Depends
from app.models.chat import ChatRequest
from app.services.chat_service import ChatService

router = APIRouter()


@router.post("/")
async def chat(request: ChatRequest,chat_service: ChatService = Depends(ChatService)):
    """Endpoint to handle chat messages."""
    reply = await chat_service.handle_user_message(
        request.conversation_id, 
        request.message
    )
    return {"reply": reply}
