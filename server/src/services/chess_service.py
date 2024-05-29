import asyncio
from typing import Dict, List, Tuple, Optional
from uuid import UUID, uuid4

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from src.database import crud, get_db, schemas
from src.services.auth_service import get_current_user
from src.utils.game import Game
from src.utils import connection_manager, matchmaker

# TODO add a leaderboard endpoint

# TODO document the code

async def __check_connection_task(connected : List[bool], websocket : WebSocket) -> Tuple[None | str, bool]:
    result = (None, False)
    try:
        while not connected[0]:
            result = (await websocket.receive_text(), False)
    except WebSocketDisconnect:
        result = (None, True)
    finally:
        return result

async def __find_match_task(user_connection : schemas.UserConnection) -> Tuple[None | Game, bool]:
    return await matchmaker.find_game(user_connection), False

async def join_game(websocket: WebSocket, token: str, db: Session):
    connection_id = await connection_manager.connect(websocket)
    user = await get_current_user(token, db)
    user_connection = schemas.UserConnection(
        connection_id=connection_id, **user.model_dump()
    )

    connected = [False]

    await websocket.send_json(
        {
            "status": "waiting",
            "connection_id": str(connection_id),
        }
    )

    task1 = asyncio.create_task(__check_connection_task(connected, websocket))
    task2 = asyncio.create_task(__find_match_task(user_connection))

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
        connected[0] = [True]

        try:
            move, _ = await pending_task

            while game.winner is None and move is not None:
                await game.push_move(user_connection, move)
                move = await websocket.receive_text()
        except (WebSocketDisconnect, RuntimeError) as e:
            pass

        print(f"{connection_id} disconnected")
        await game.disconnect(user_connection)
        connection_manager.disconnect(connection_id)
