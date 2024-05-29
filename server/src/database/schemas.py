from datetime import date, datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    username: str = Field(
        title="The username.", pattern="^\w+$", examples=["john_doe123"]
    )
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(
        title="The password.",
        max_length=255,
        min_length=8,
    )


class UserDetails(BaseModel):
    date_of_birth: Optional[date] = None
    elo_rating: int = 1200
    wins: int = 0
    losses: int = 0
    draws: int = 0

    games_played: int = 0

    class Config:
        from_attributes = True


class User(UserBase):
    id: int
    details: UserDetails

    class Config:
        from_attributes = True


class UserConnection(User):
    connection_id: UUID


class GameState(BaseModel):
    fen: str
    player_turn: str = "W"
    last_move: Optional[str] = None
    legal_moves: List[str] = []
    winner: Optional[str] = None


class GameResponse(GameState):
    success: bool


class Game(BaseModel):
    white_player_id: int
    black_player_id: int
    moves: List[str]
    winner: Optional[int]
    date: datetime = Field(default_factory=datetime.now)

    white_player: User
    black_player: User

    class Config:
        from_attributes = True
        populate_by_name = True
        use_enum_values = True
