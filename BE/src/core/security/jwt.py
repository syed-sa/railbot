from datetime import datetime, timedelta, timezone
from jose import JWTError, ExpiredSignatureError, jwt
from fastapi import HTTPException, status

class JWTManager:
    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        access_exp_minutes: int,
        refresh_exp_days: int,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_exp = access_exp_minutes
        self.refresh_exp = refresh_exp_days

    def _create_token(
        self,
        subject: str,
        expires_delta: timedelta,
        token_type: str,
    ) -> str:
        expire = datetime.now(timezone.utc) + expires_delta
        payload = {
            "sub": subject,
            "type": token_type,
            "exp": expire,
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_access_token(self, user_id: str) -> str:
        return self._create_token(
            subject=user_id,
            expires_delta=timedelta(minutes=self.access_exp),
            token_type="access",
        )

    def create_refresh_token(self, user_id: str) -> str:
        return self._create_token(
            subject=user_id,
            expires_delta=timedelta(days=self.refresh_exp),
            token_type="refresh",
        )

    def decode(self, token: str) -> dict:
        try:
            return jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )

        except ExpiredSignatureError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            ) from exc

        except JWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            ) from exc