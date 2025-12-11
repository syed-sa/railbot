""""API endpoints for chat interactions.
"""
from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.responses import StreamingResponse
from app.models.chat import ChatRequest
from app.services.chat.chat_service import ChatService
from dependency_injector.wiring import inject, Provide

router = APIRouter()


@router.post("/")
async def chat(request: ChatRequest,    chat_service: ChatService = Depends(Provide[Container.chat_service])
):
    
    async def event_gen():
        async for token in chat_service.handle_user_message(
            request.conversation_id,
            request.message
        ):
            yield f"data: {token}\n\n"
    
    return StreamingResponse(event_gen(), media_type="text/event-stream")

@router.post("/stream")
async def chat_stream(request: ChatRequest, chat_service: ChatService = Depends(ChatService)):

    async def event_gen():
        async for token in chat_service.stream_reply(
            request.conversation_id,
            request.message
        ):
            yield f"data: {token}\n\n"
    
    return StreamingResponse(event_gen(), media_type="text/event-stream")
    