from fastapi import Depends, HTTPException, status
from sqlalchemy import event, or_
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
    email = user.email
    username = user.username

    if (existing_user := db.query(models.User).filter(or_(models.User.email == email, models.User.username == username)).first()):
        msg = "Username already in use." if existing_user.username == username else "Email already in use."
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=msg
        )

    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def create_game(game: schemas.Game, db: Session = Depends(get_db)) -> models.Game:
    db_game = models.Game(
        **game.model_dump(exclude=('id', 'white_player', 'black_player')))

    db.add(db_game)
    db.commit()
    db.refresh(db_game)

    return db_game


def create_game_player(player: schemas.GamePlayer, game_object: models.Game, db: Session = Depends(get_db)):
    db_player = models.GamePlayer(
        **player.model_dump(), game=game_object
    )

    db.add(db_player)
    db.commit()
    db.refresh(db_player)

    return db_player


def get_user_games(user: schemas.User, db: Session = Depends(get_db)):
    games = db.query(models.Game).filter(
        (models.Game.white_player_id == user.id) | (
            models.Game.black_player_id == user.id)
    ).all()

    games = [(game, db.query(models.GamePlayer).filter(
        (models.GamePlayer.player_id == user.id) & (models.GamePlayer.game_id == game.game_id)).first()) for game in games]

    game_views = [schemas.GameView(
        game_id=game.game_id,
        opponent=game.white_player if game.black_player_id == user.id else game.black_player,
        winner=game.winner,
        date=game.date,
        gained_elo=game_player.gained_elo
    ) for game, game_player in games]

    return game_views[::-1]


def get_game_by_id(id: int, db: Session = Depends(get_db)):
    if game := db.query(models.Game).filter(models.Game.game_id == id).first():
        return game
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found"
        )


@event.listens_for(models.User, "after_insert")
def __create_user_details(mapper, connection, target):
    db = Session(bind=connection)

    db.add(models.UserDetails(id=target.id))
    db.commit()


@event.listens_for(models.GamePlayer, "after_insert")
def __update_user_elo(mapper, connection, target):
    db = Session(bind=connection)

    player = db.query(models.UserDetails).filter(
        models.UserDetails.id == target.player_id).first()

    if target.game.winner == target.player_id:
        player.wins += 1
    elif target.game.winner is None:
        player.draws += 1
    else:
        player.losses += 1

    player.elo_rating += target.gained_elo

    db.flush()
    db.commit()
