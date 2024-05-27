from database import get_db, models, schemas


from fastapi import Depends, HTTPException, status
from sqlalchemy import event
from sqlalchemy.orm import Session


from typing import Annotated


def get_user_by_username(username: str, db: Session = Depends(get_db)):
    if user := db.query(models.User).filter(models.User.username == username).first():
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

def get_user_by_id(id : int, db :Session = Depends(get_db)) -> models.User:
    if user :=db.query(models.User).filter(models.User.id == id).first():
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )


def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

def create_game(game: schemas.Game, db: Session = Depends(get_db)):
    db_game = models.Game(**game.model_dump())
    db.add(db_game)
    db.commit()
    db.refresh(db_game)

    return db_game

@event.listens_for(models.Game, "after_insert")
def __game_update_user_details(mapper, connection, target):
    db = Session(bind=connection)

    white_user = get_user_by_id(target.white_player, db)
    black_user = get_user_by_id(target.black_player, db)

    if target.winner is None:
        white_user.details.draws += 1
        black_user.details.draws += 1
    elif target.winner == target.white_player:
        white_user.details.wins += 1
        black_user.details.losses += 1
    else:
        white_user.details.losses += 1
        black_user.details.wins += 1

    db.flush()

@event.listens_for(models.User, "after_insert")
def __create_user_details(mapper, connection, target):
    db = Session(bind=connection)

    db.add(models.UserDetails(id=target.id))
    db.commit()
