from uuid import uuid4
from fastapi import HTTPException

from app.core.security.jwt import JWTManager


class AuthService:
    def __init__(
        self,
        refresh_repo: RefreshTokenRepository,
        jwt_manager: JWTManager,
    ):
        self.refresh_repo = refresh_repo
        self.jwt = jwt_manager


    async def refresh_token(self, db, refresh_token: str):
        payload = self.jwt.decode(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token")

        token_record = await self.refresh_repo.get_valid_by_user(
            db, user_id=payload["sub"]
        )

        if not token_record or not self.jwt.verify_refresh_token(
            refresh_token, token_record.token_hash
        ):
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # rotation
        

        new_access = self.jwt.create_access_token(payload["sub"])
        new_refresh = self.jwt.create_refresh_token(payload["sub"])
        async with db.begin():
            await self.refresh_repo.delete(db, token_record.id)
            await self.refresh_repo.create(
                db,
                id=str(uuid4()),
                user_id=payload["sub"],
                token_hash=self.jwt.hash_refresh_token(new_refresh),
                expires_at=token_record.expires_at,
            )


        return {
            "access_token": new_access,
            "refresh_token": new_refresh,
            "token_type": "bearer",
        }
