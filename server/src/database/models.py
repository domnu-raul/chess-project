from sqlalchemy import CheckConstraint, String, ForeignKey, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship, column_property
from typing import List, Optional
from datetime import date, datetime

from src.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str]
    details: Mapped["UserDetails"] = relationship(
        back_populates="user", cascade="all, delete"
    )


class UserDetails(Base):
    __tablename__ = "user_details"

    id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    user: Mapped["User"] = relationship(back_populates="details")

    date_of_birth: Mapped[Optional[date]] = mapped_column(default=None)

    elo_rating: Mapped[int] = mapped_column(default=1200)

    wins: Mapped[int] = mapped_column(default=0)
    losses: Mapped[int] = mapped_column(default=0)
    draws: Mapped[int] = mapped_column(default=0)
    games_played = column_property(wins + losses + draws)


class Game(Base):
    __tablename__ = "game_logs"

    game_id: Mapped[int] = mapped_column(primary_key=True)
    white_player_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    black_player_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    moves: Mapped[List[str]] = mapped_column(ARRAY(String(5)))
    winner: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    date: Mapped[datetime] = mapped_column(default=datetime.now)

    white_player: Mapped["User"] = relationship(
        "User", foreign_keys=[white_player_id])
    black_player: Mapped["User"] = relationship(
        "User", foreign_keys=[white_player_id])
