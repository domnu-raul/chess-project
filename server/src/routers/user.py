from fastapi import APIRouter, Depends
from src.services import auth_service
from src.database.models import User
from src.database import crud, get_db

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/me")
def get_user_details(user: User = Depends(auth_service.get_current_user)):

    return user.model_dump()

@router.get("/games")
def get_user_games(user: User = Depends(auth_service.get_current_user), db = Depends(get_db)):

    return crud.get_user_games(user, db)
