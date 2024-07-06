import os
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from typing import List
from src.services import auth_service
from src.database.models import User
from src.database import crud, get_db, schemas

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me")
def get_my_details(user: User = Depends(auth_service.get_current_user), db=Depends(get_db)) -> schemas.User:
    return get_user_details(user.id, db)


@router.get("/me/picture")
def get_my_picture(user: User = Depends(auth_service.get_current_user), db=Depends(get_db)) -> FileResponse:
    return get_user_picture(user.id)


@router.post("/me/picture")
async def upload_profile_picture(file: UploadFile = File(...), user: User = Depends(auth_service.get_current_user), db=Depends(get_db)):
    directory = "public/profiles"
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = f"{directory}/{user.id}.png"
    if os.path.exists(file_path):
        os.remove(file_path)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    return {"file_path": file_path}


@router.get("/{id}/picture")
def get_user_picture(id: int, db=Depends(get_db)) -> FileResponse:
    path = f"public/profiles/{id}.png"
    if not os.path.exists(path):
        path = "public/profiles/default.png"
    return FileResponse(path)


@router.get("/{user_id}")
def get_user_details(user_id: int, db=Depends(get_db)) -> schemas.User:
    return crud.get_user_by_id(user_id, db)


@router.get("/games")
def get_user_games(user: User = Depends(auth_service.get_current_user), db=Depends(get_db)) -> List[schemas.Game]:
    return crud.get_user_games(user, db)
