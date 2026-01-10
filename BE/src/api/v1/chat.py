""""API endpoints for chat interactions.
"""
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.responses import StreamingResponse
from app.container import Container
from app.schema.chat_schema import ChatRequest
from app.service.chat.chat_service import ChatService

router = APIRouter()


@router.post("/")
@inject
async def chat(request: ChatRequest,    chat_service: ChatService = Depends(Provide[Container.chat_service])
):
    
    async def event_gen():
        async for token in chat_service.handle_user_message(
            request.conversation_id,
            request.message
        ):
            yield f"data: {token}\n\n"
    
    return StreamingResponse(event_gen(), media_type="text/event-stream")
