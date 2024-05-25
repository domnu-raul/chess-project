from database import get_db, models, schemas


from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session


from typing import Annotated


def get_user_from_db(username: str, db: Annotated[Session, Depends(get_db)]):
    if (
        user := db.query(models.UserDB)
        .filter(models.UserDB.username == username)
        .first()
    ):
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )


def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.UserDB(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
