from fastapi import APIRouter, Depends
from typing import List
from src.services import auth_service
from src.database.models import User
from src.database import crud, get_db, schemas

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/me")
def get_user_details(user: User = Depends(auth_service.get_current_user)) -> schemas.User:
    return user

@router.get("/games")
def get_user_games(user: User = Depends(auth_service.get_current_user), db = Depends(get_db)) -> List[schemas.Game]:

    return crud.get_user_games(user, db)
