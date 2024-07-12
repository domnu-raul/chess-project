import asyncio
from typing import Dict, List, Tuple, Optional
from uuid import UUID, uuid4
import uuid

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from src.database import crud, get_db, schemas
from src.services.auth_service import get_current_user
from src.utils.game import Game
from src.utils import connection_manager, matchmaker

# TODO add a leaderboard endpoint

# TODO document the code


async def __check_connection_task(connected: List[bool], websocket: WebSocket) -> Tuple[None | str, bool]:
    result = (None, False)
    try:
        while not connected[0]:
            result = (await websocket.receive_text(), False)
    except WebSocketDisconnect:
        result = (None, True)
    finally:
        return result


async def __find_match_task(user_connection: schemas.UserConnection) -> Tuple[None | Game, bool]:
    return await matchmaker.find_game(user_connection), False


async def find_game(websocket: WebSocket, token: str, db: Session):
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
        await connection_manager.disconnect(connection_id)
        return

    if type(game_id := result) is uuid.UUID:
        print(f"{connection_id} found a match")
        connected[0] = [True]

        try:
            await connection_manager.send_json_to(connection_id, {
                "status": "found",
                "game_id": str(game_id),
            })
            await connection_manager.disconnect(connection_id)
            _, _ = await pending_task

        except (WebSocketDisconnect, RuntimeError) as e:
            pass

        print(f"{connection_id} disconnected")


async def join_game(websocket: WebSocket, token: str, game_id: str, db: Session):
    connection_id = await connection_manager.connect(websocket)
    user = await get_current_user(token, db)
    user_connection = schemas.UserConnection(
        connection_id=connection_id, **user.model_dump()
    )

    game = Game.get_hashed(uuid.UUID(game_id))
    game.join(user_connection)

    while not game.game_state.is_end:
        try:
            msg = await websocket.receive_text()
            await game.push_msg(user_connection, msg)
        except WebSocketDisconnect:
            await game.disconnect(user_connection)
            print(f"{connection_id} disconnected")
            return

    await game.disconnect(user_connection)
    await connection_manager.disconnect(connection_id)
    print(f"{connection_id} disconnected")
