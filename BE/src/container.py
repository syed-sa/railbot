# app/container.py
from dependency_injector import containers, providers
from redis import Redis
from app.core.security.jwt import JWTManager
from app.core.security.password import passwordManager
from app.repository.auth_repository import AuthRepository
from app.repository.user_repository import UserRepository
from app.core.config import get_settings
from app.service.auth.auth_service import AuthService
from app.service.llm.llm_client import LLMClient
from app.service.user.user_service import UserService
from app.service.chat.chat_service import ChatService
from app.service.redis.state_manager import StateManager
from app.service.irctc.irctc_client import IRCTCClient  
from app.service.llm.llm_service import LLMService
class Container(containers.DeclarativeContainer):

    settings = get_settings()
    # Repositories
    user_repository = providers.Singleton(UserRepository)
    auth_repository = providers.Singleton(AuthRepository)
    llm_client = providers.Singleton(
        LLMClient,
        api_url=settings.HF_API_URL,
        api_key=settings.HF_API_KEY,
        model_name=settings.HF_MODEL_NAME,
    )
    irctc_client = providers.Singleton(IRCTCClient,settings.IRCTC_API_KEY,settings.RAPIDAPI_HOST)
    llm_service = providers.Singleton(LLMService, llm_client=llm_client)
    redis_client = providers.Singleton(
        Redis,
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True,
        max_connections=10,
    )

    state_manager = providers.Singleton(
        StateManager,
        redis=redis_client,
        ttl=settings.REDIS_TTL,
        max_history=20,
    )
    # Security
    jwt_manager = providers.Singleton(
        JWTManager,
        secret_key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
        access_exp_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_exp_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )

    password_manager = providers.Singleton(passwordManager)

    # Services
    user_service = providers.Factory(
        UserService,
        repo=user_repository,
        auth_repository=auth_repository,
        jwt_manager=jwt_manager,
        password_manager=password_manager,
    )

    auth_service = providers.Factory(
        AuthService,
        auth_repository=auth_repository,
        jwt_manager=jwt_manager,
    )

    chat_service = providers.Factory(
        ChatService,
        state=state_manager,   
        irctc_client=irctc_client,
        llm_service=llm_service
    )


