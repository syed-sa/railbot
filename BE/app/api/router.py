# app/api/router.py

from fastapi import APIRouter
from app.api.v1.chat import router as chat_router
from app.api.v1.user import router as user_router

api_router = APIRouter()

api_router.include_router(chat_router, prefix="/chat", tags=["Chat"])
api_router.include_router(user_router, prefix="/user", tags=["User"])