#mdel/user.py
from sqlalchemy import Boolean, Column, Integer, String,ForeignKey,DateTime
from app.db.base import Base
from sqlalchemy.sql import func
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Integer, default=1)



class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True)

    token_hash = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    revoked = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now)
