from fastapi import Depends
from dependency_injector.wiring import inject, Provide
from app.api import router
from app.container import Container
from sqlalchemy.orm import Session
from app.main import get_db
from app.schemas.user_schema import UserCreate, UserResponse
from app.services.user_service import UserService

@router.post("/signup", response_model=UserResponse)
@inject
def signup(
    payload: UserCreate,
    db: Session = Depends(get_db),
    user_service: UserService = Depends(Provide[Container.user_service])
):
    return user_service.signup(db, payload)
