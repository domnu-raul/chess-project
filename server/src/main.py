from fastapi import Depends, FastAPI, Query, WebSocket

from sqlalchemy.orm import Session

from services import chess_service
from database import init_db, get_db
from routers import auth

app = FastAPI()
init_db()

app.include_router(auth.router)


@app.websocket("/play")
async def __play__(
    websocket: WebSocket,
    token: str = Query(alias="token"),
    db: Session = Depends(get_db),
):
    return await chess_service.join_game(websocket, token, db)
