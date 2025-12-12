from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import hash_password
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate

class UserService:

    def __init__(self, repo: UserRepository):
        self.repo = repo

    def signup(self, db: Session, data: UserCreate):
        existing = self.repo.get_by_email(db, data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        hashed = hash_password(data.password)
        return self.repo.create(db, data.email, hashed)
