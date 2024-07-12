from datetime import date, datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    username: str = Field(
        title="The username.", pattern="^\w+$", examples=["john_doe123"]
    )
    email: EmailStr

    class Config:
        from_attributes = True


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


class UserConnection(User):
    connection_id: UUID


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenResponse(BaseModel):
    user: UserBase
    token: Token

    class Config:
        from_attributes = True


class GameState(BaseModel):
    fen: str
    turn: str = "W"
    last_move: Optional[str] = None
    legal_moves: List[str] = []
    winner: Optional[str] = None
    is_end: bool = False


class GameUpdate(GameState):
    color: str
    black_player_id: int
    white_player_id: int


class ChatUpdate(BaseModel):
    sender_id: int
    message: str


class GameResponse(BaseModel):
    success: bool
    type: str
    content: GameUpdate | ChatUpdate


class GamePlayer(BaseModel):
    game_id: Optional[int]
    player_id: int
    gained_elo: int

    class Config:
        from_attributes = True


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


class GameView(BaseModel):
    game_id: int
    opponent: User
    winner: Optional[int]
    gained_elo: int
    date: datetime

    class Config:
        from_attributes = True
        populate_by_name = True
        use_enum_values = True
