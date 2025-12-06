from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router

def create_app():
    app = FastAPI(title="Train-Info Chatbot", version="1.0.0")
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # React default
            "http://localhost:5173",  # Vite default
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],  # Allows OPTIONS, POST, GET, etc.
        allow_headers=["*"],  # Allows Content-Type, Accept, etc.
    )
    
    app.include_router(api_router, prefix="/api/v1")
    return app

app = create_app()