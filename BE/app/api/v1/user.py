from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from app.container import Container
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dep import get_db
from app.schema.user_schema import UserCreate, UserResponse
from app.service.user.user_service import UserService

router = APIRouter()


@router.post("/signup", response_model=UserResponse)
@inject
async def signup(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    return await user_service.signup(db, payload)
