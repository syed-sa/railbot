import app.model.models
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone

class AuthRepository:

    async def store_refresh_token(self, db: AsyncSession, user_id: int, refresh_token: str):

        RefreshToken = app.model.models.RefreshToken(
            user_id=user_id,
            token_hash=refresh_token,
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            revoked=False,
            created_at=datetime.now(timezone.utc)
        )