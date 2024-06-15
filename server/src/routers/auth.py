from datetime import timedelta
from fastapi import APIRouter, Body, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session
from typing import Annotated

from src.database import schemas, get_db
from src.database.crud import create_user
from src.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> schemas.TokenResponse:
    user = auth_service.authenticate_user(
        form_data.username, form_data.password, db)

    access_token_expires = timedelta(days=auth_service.TOKEN_EXPIRATION_DAYS)
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    response.set_cookie(key="access_token", value=access_token, httponly=True,
                        max_age=auth_service.TOKEN_EXPIRATION_DAYS * 24 * 60 * 60)

    return schemas.TokenResponse(user=user, token=schemas.Token(access_token=access_token, token_type="bearer"))


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
) -> schemas.TokenResponse:
    return schemas.TokenResponse(user=user, token=schemas.Token(access_token=token, token_type="bearer"))
