from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.core.security.jwt import JWTManager
from app.core.security.password import hash_password
from app.repository.user_repository import UserRepository
from app.schema.user_schema import UserCreate
from app.service.auth.auth_service import AuthService

class UserService:

    def __init__(self, repo: UserRepository, jwt_manager: JWTManager):
        self.repo = repo
        self.jwt_manager = jwt_manager

    async def signup(self, db: AsyncSession, data: UserCreate):
        existing = await self.repo.get_by_email(db, data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        hashed = hash_password(data.password)
        return await self.repo.create(db, data.email, hashed)

    async def login(self,db: AsyncSession, data: UserCreate):
        user = await self.repo.get_by_email(db, data.email)
        if not user or not self.repo.verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        access_token = self.jwt_manager.create_access_token(str(user.id))
        refresh_token = self.jwt_manager.create_refresh_token(str(user.id))
        self.repo.store_refresh_token(db, user.id, hash_password(refresh_token))
        return {"access_token": access_token, "refresh_token": refresh_token, "user": user}
    
    async def refresh_token(self, db: AsyncSession, token: str):
        return await AuthService.refresh_token(self, db, token)