import asyncio
import bisect
import threading
from typing import Dict, List, Tuple, Optional
from uuid import UUID, uuid4

import chess
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from src.database import crud, get_db, schemas
from src.services.auth_service import get_current_user
from src.utils.game import Game
from src.utils import connection_manager, matchmaker

# TODO move ConnectionManager to a separate file

# TODO add a leaderboard endpoint

# TODO document the code

async def join_game(websocket: WebSocket, token: str, db: Session):
    connection_id = await connection_manager.connect(websocket)
    user = await get_current_user(token, db)
    user_connection = schemas.UserConnection(
        connection_id=connection_id, **user.model_dump()
    )

    connected = False

    async def check_connection_task() -> Tuple[None | str, bool]:
        result = (None, False)
        try:
            while not connected:
                result = (await websocket.receive_text(), False)
        except WebSocketDisconnect:
            result = (None, True)
        finally:
            return result

    async def find_match_task() -> Tuple[None | Game, bool]:
        return await matchmaker.find_game(user_connection), False

    await websocket.send_json(
        {
            "status": "waiting",
            "connection_id": str(connection_id),
        }
    )

    task1 = check_connection_task()
    task2 = find_match_task()

    done, pending = await asyncio.wait(
        [task1, task2], return_when=asyncio.FIRST_COMPLETED
    )
    done_task = done.pop()
    result, connection_closed = done_task.result()

    pending_task = pending.pop()

    if connection_closed:
        print(f"{connection_id} disconnected")
        connection_manager.disconnect(connection_id)
        return

    if type(game := result) is Game:
        game.join(user_connection)
        connected = True

        try:
            move, _ = await pending_task

            while game.get_winner() is None and move is not None:
                await game.push_move(user_connection, move)
                move = await websocket.receive_text()
        except (WebSocketDisconnect, RuntimeError) as e:
            pass

        print(f"{connection_id} disconnected")
        await game.disconnect(user_connection)
        connection_manager.disconnect(connection_id)
