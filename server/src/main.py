from fastapi import Depends, FastAPI, Header, WebSocket

from sqlalchemy.orm import Session

from services import play_service
from database import init_db, get_db
from routers import auth

app = FastAPI()
init_db()

app.include_router(auth.router)


@app.websocket("/play")
async def __play__(
    websocket: WebSocket,
    token: str = Header(alias="Token"),
    db: Session = Depends(get_db),
):
    return await play_service.join_game(websocket, token, db)
