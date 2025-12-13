from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.core.security import hash_password
from app.repository.user_repository import UserRepository
from app.schema.user_schema import UserCreate


class UserService:

    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def signup(self, db: AsyncSession, data: UserCreate):
        existing = await self.repo.get_by_email(db, data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        hashed = hash_password(data.password)
        return await self.repo.create(db, data.email, hashed)
