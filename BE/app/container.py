# app/container.py
from dependency_injector import containers, providers
from app.core.security.jwt import JWTManager
from app.core.security.password import passwordManager
from app.repository.auth_repository import AuthRepository
from app.repository.user_repository import UserRepository
from app.core.config import get_settings
from app.service.auth.auth_service import AuthService
from app.service.user.user_service import UserService
from app.service.chat.chat_service import ChatService
class Container(containers.DeclarativeContainer):

    settings = get_settings()
    # Repositories
    user_repository = providers.Singleton(UserRepository)
    auth_repository = providers.Singleton(AuthRepository)

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
    )