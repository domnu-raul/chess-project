import uvicorn
from fastapi import Depends, FastAPI, Query, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from src.routers import auth, user
from src.services import chess_service
from src.database import get_db, init_db

app = FastAPI()
origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(auth.router)
app.include_router(user.router)


@app.websocket("/matchmaking")
async def __find_match__(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db),
):
    return await chess_service.find_game(websocket, token, db)


@app.websocket("/game/{game_id}")
async def __play__(
    game_id: str,
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db),
):
    return await chess_service.join_game(websocket, token, game_id, db)

if __name__ == "__main__":
    uvicorn.run('src.main:app', reload=True)
