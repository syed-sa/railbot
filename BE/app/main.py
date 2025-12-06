from fastapi import FastAPI
from app.api.router import api_router

def create_app():
    app = FastAPI(title="Train-Info Chatbot", version="1.0.0")
    app.include_router(api_router, prefix="/api/v1")
    return app

app = create_app()
