from fastapi import Depends, HTTPException, status
from sqlalchemy import event
from sqlalchemy.orm import Session
from src.database import get_db, models, schemas


from typing import Annotated


def get_user_by_username(username: str, db: Session = Depends(get_db)):
    if user := db.query(models.User).filter(models.User.username == username).first():
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )


def get_user_by_id(id: int, db: Session = Depends(get_db)) -> models.User:
    if user := db.query(models.User).filter(models.User.id == id).first():
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


def create_game(game: schemas.Game, db: Session = Depends(get_db)) -> models.Game:
    db_game = models.Game(
        **game.model_dump(exclude=('id', 'white_player', 'black_player')))

    db.query(models.UserDetails).filter(models.UserDetails.id == game.white_player.id).update(
        game.white_player.details.model_dump(exclude=('games_played',))
    )

    db.query(models.UserDetails).filter(models.UserDetails.id == game.black_player.id).update(
        game.black_player.details.model_dump(exclude=('games_played',))
    )

    db.flush()

    db.add(db_game)
    db.commit()
    db.refresh(db_game)

    return db_game

def get_user_games(user: schemas.User, db: Session = Depends(get_db)):
    games = db.query(models.Game).filter(
        (models.Game.white_player_id == user.id) | (models.Game.black_player_id == user.id)
    ).all()

    return games


@event.listens_for(models.User, "after_insert")
def __create_user_details(mapper, connection, target):
    db = Session(bind=connection)

    db.add(models.UserDetails(id=target.id))
    db.commit()
