from fastapi import Depends, FastAPI, Query, WebSocket
from sqlalchemy.orm import Session

from src.routers import auth
from src.services import chess_service
from src.database import get_db, init_db

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', reload=True)
