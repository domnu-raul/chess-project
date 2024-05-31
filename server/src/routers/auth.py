from datetime import timedelta
from fastapi import APIRouter, Body, Depends
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session
from typing import Annotated

from src.database import schemas, get_db
from src.database.crud import create_user
from src.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    user = auth_service.authenticate_user(
        form_data.username, form_data.password, db)

    access_token_expires = timedelta(days=auth_service.TOKEN_EXPIRATION_DAYS)
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return auth_service.Token(access_token=access_token, token_type="bearer")


@router.post("/register")
async def register_account(
    user_data: Annotated[schemas.UserCreate, Body()],
    db: Session = Depends(get_db),
) -> schemas.User:
    return auth_service.register_user(user_data, db)


@router.get("/token")
async def read_users_me(
    token: str = Depends(auth_service.oauth2_scheme),
    user: schemas.UserBase = Depends(auth_service.get_current_user),
):
    return {"token": token, "user:": user}
