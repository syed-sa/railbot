# app/container.py
from dependency_injector import containers, providers

from app.services.chat.chat_service import ChatService
from app.services.irctc.irctc_client import IRCTCClient
from app.services.llm.llm_client import LLMClient
from app.services.llm.llm_service import LLMService
from app.services.redis.state_manager import StateManager
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService


from app.core.config import get_settings

settings = get_settings()


class Container(containers.DeclarativeContainer):

    wiring_config = containers.WiringConfiguration(
    modules=[
        "app.api.v1.chat",
        "app.api.v1.user",   
    ]
)

    # Redis
    state_manager = providers.Singleton(
        StateManager,
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
    )

    # IRCTC
    irctc_client = providers.Singleton(
        IRCTCClient,
        api_key=settings.IRCTC_API_KEY,
        host=settings.RAPIDAPI_HOST,
        timeout=20.0,
    )

    # LLM Client
    llm_client = providers.Singleton(
        LLMClient,
        api_url=settings.HF_API_URL,
        api_key=settings.HF_API_KEY,
        model_name=settings.HF_MODEL_NAME,
    )

    # LLM Service
    llm_service = providers.Singleton(LLMService, llm_client=llm_client)

    # Chat Service
    chat_service = providers.Factory(
        ChatService,
        state=state_manager,
        irctc_client=irctc_client,
        llm_service=llm_service,
    )


    # User Repository
    user_repository = providers.Singleton(UserRepository)

    # User Service
    user_service = providers.Factory(UserService, repo=user_repository)
