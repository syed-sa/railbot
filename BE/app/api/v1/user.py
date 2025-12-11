from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from app.container import Container
from app.api.schemas import UserCreate
from app.api.services import UserService

router = APIRouter()


@router.post("/signup")
@inject
async def signup(
    user_data: UserCreate,
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    user = await user_service.create_user(user_data)
    return user
