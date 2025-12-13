from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.container import Container
from rich.traceback import install
install(show_locals=True)
def create_app():
    app = FastAPI(title="Train-Info Chatbot", version="1.0.0")

    container = Container()
    app.container = container

    container.wire(modules=[
    "app.api.v1.user",
    "app.api.v1.chat",
    ])

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api/v1")

    return app

app = create_app()
