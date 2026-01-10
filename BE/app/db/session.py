from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import get_settings

settings = get_settings()
# Use async engine for the `postgresql+asyncpg` dialect; remove sqlite-specific args
engine = create_async_engine(settings.POSTGRES_URI, echo=False)
SessionLocal = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
