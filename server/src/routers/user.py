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


@router.get("/{id}/picture")
def get_user_picture(id: int, db=Depends(get_db)) -> FileResponse:
    return FileResponse(f"public/profiles/{id}.png")


@router.get("/{user_id}")
def get_user_details(user_id: int, db=Depends(get_db)) -> schemas.User:
    return crud.get_user_by_id(user_id, db)


@router.get("/games")
def get_user_games(user: User = Depends(auth_service.get_current_user), db=Depends(get_db)) -> List[schemas.Game]:
    return crud.get_user_games(user, db)


@router.post("/upload-profile")
async def upload_profile_picture(file: UploadFile = File(...), user: User = Depends(auth_service.get_current_user), db=Depends(get_db)):
    file_path = f"public/profiles/{user.id}.png"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    return {"file_path": file_path}
