from typing import Tuple, List, Dict
import asyncio
import threading
import chess

from dataclasses import dataclass
from uuid import UUID, uuid4

import database
from services.auth_service import get_current_user
from sqlalchemy.orm import Session

from fastapi import WebSocket, WebSocketDisconnect

from database import schemas, crud
import bisect

# TODO move ConnectionManager to a separate file

# TODO add a leaderboard endpoint

# TODO document the code, remove print() calls


@dataclass
class ConnectionManager:
    connections: Dict[UUID, Tuple[WebSocket, schemas.User]]

    def __init__(self):
        self.connections = dict()

    async def connect(self, websocket: WebSocket) -> UUID:
        connection_id = uuid4()

        await websocket.accept()

        self.connections[connection_id] = websocket
        return connection_id

    def disconnect(self, connection_id: UUID) -> None:
        self.connections.pop(connection_id)

    async def send_message_to(self, connection_id: UUID, message: str):
        await self.connections[connection_id].send_text(message)

    async def send_json_to(self, connection_id: UUID, json: dict):
        try:
            await self.connections[connection_id].send_json(json)
        except KeyError:
            print(f"Connection {connection_id} not found")


class Matchmaker:
    waiting_queue: List[Tuple[schemas.UserConnection, asyncio.Queue]]
    MATCHMAKING_RANGE = 100

    def __init__(self):
        self.waiting_queue = list()
        threading.Thread(target=self.matchmaking, daemon=True).start()

    def __add(self, user: schemas.UserConnection):
        queue = asyncio.Queue()
        bisect.insort(
            self.waiting_queue, (user, queue), key=lambda o: o[0].details.elo_rating
        )

        return queue

    def matchmaking(self):
        while True:
            if len(self.waiting_queue) >= 2:
                for i in range(0, len(self.waiting_queue) - 1):
                    player_a, queue_a = self.waiting_queue[i]
                    player_b, queue_b = self.waiting_queue[i + 1]
                    if (
                        abs(player_a.details.elo_rating - player_b.details.elo_rating)
                        <= self.MATCHMAKING_RANGE
                    ):
                        self.waiting_queue.pop(i)
                        self.waiting_queue.pop(i)

                        game = Game()
                        queue_a.put_nowait(game)
                        queue_b.put_nowait(game)

    async def find_game(self, user: schemas.UserConnection):
        queue = self.__add(user)

        game = await queue.get()
        return game


@dataclass
class Game:
    board: chess.Board
    black: schemas.UserConnection | None = None
    white: schemas.UserConnection | None = None
    game_state: schemas.GameState | None = None
    pushed_move: Tuple[schemas.UserConnection, str] | None = None

    def __init__(self):
        self.board = chess.Board()
        self.__update_state()

        def run_in_new_loop(loop, coro):
            asyncio.set_event_loop(loop)
            loop.run_until_complete(coro)
            loop.close()

        new_loop = asyncio.new_event_loop()
        threading.Thread(
            target=run_in_new_loop, args=(new_loop, self.engine()), daemon=True
        ).start()

    def join(self, player: schemas.UserConnection):
        if self.white is None:
            self.white = player
        elif self.black is None:
            self.black = player
        else:
            raise Exception("Game is full")

    async def engine(self):
        while self.black is None or self.white is None:
            await asyncio.sleep(1)

        await connectionManager.send_json_to(
            self.white.connection_id,
            dict(
                self.__get_response_for_player(self.white, True).model_dump(), color="W"
            ),
        )

        await connectionManager.send_json_to(
            self.black.connection_id,
            dict(
                self.__get_response_for_player(self.black, True).model_dump(), color="B"
            ),
        )

        while self.game_state.winner is None:
            if (t := self.pushed_move) is not None:
                player, move = t
                self.board.push(chess.Move.from_uci(move))

                self.__update_state(last_move=move)
                self.pushed_move = None

                response = self.__get_response_for_player(self.black, True)
                other_player = self.white if player == self.black else self.black

                await connectionManager.send_json_to(
                    other_player.connection_id,
                    self.__get_state_for_player(other_player).model_dump(),
                )

                await connectionManager.send_json_to(
                    player.connection_id,
                    response.model_dump(),
                )


        final_state = self.game_state.model_dump()

        await connectionManager.send_json_to(self.black.connection_id, final_state)
        await connectionManager.send_json_to(self.white.connection_id, final_state)

        game_model = schemas.Game(
            white_player=self.white.id,
            black_player=self.black.id,
            moves = [move.uci() for move in self.board.move_stack],
            winner=None if self.game_state.winner is None else self.white.id if self.game_state.winner == "W" else self.black.id,
        )

        crud.create_game(game_model, next(database.get_db()))

    async def push_move(self, player: schemas.UserConnection, move: str):
        if self.__is_valid_move(move) and self.__is_player_turn(player):
            self.pushed_move = (player, move)
        else:
            response = self.__get_response_for_player(player, False)

            await connectionManager.send_json_to(
                player.connection_id,
                response.model_dump(),
            )

    def __get_response_for_player(self, player: schemas.UserConnection, success: bool):
        response = schemas.GameResponse(
            success=success, **self.__get_state_for_player(player).model_dump()
        )

        return response

    def __get_state_for_player(self, player: schemas.UserConnection):
        state = self.game_state.model_dump()
        if not self.__is_player_turn(player):
            state["legal_moves"] = []

        return schemas.GameState(**state)

    def __is_player_turn(self, player: schemas.UserConnection):
        return (
            self.board.turn == chess.WHITE
            and player == self.white
            or self.board.turn == chess.BLACK
            and player == self.black
        )

    def __is_valid_move(self, move: str):
        try:
            uci_move = chess.Move.from_uci(move)
            return self.board.is_legal(uci_move)
        except chess.InvalidMoveError:
            return False

    def __update_state(self, last_move: str | None = None):
        if self.game_state is None:
            self.game_state = schemas.GameState(fen=self.board.fen())

        moves = [move.uci() for move in self.board.legal_moves]

        outcome = self.board.outcome()
        if outcome is not None:
            self.games_state.is_end = True
            self.game_state.winner = (
                "W"
                if outcome.winner == chess.WHITE
                else "B" if outcome.winner == chess.BLACK else None
            )

        self.game_state.player_turn = "W" if self.board.turn == chess.WHITE else "B"
        self.game_state.fen = self.board.fen()
        self.game_state.last_move = last_move
        self.game_state.legal_moves = moves

    async def disconnect(self, player: UUID):
        if player == self.white:
            self.game_state.winner = "B"
        else:
            self.game_state.winner = "W"

    def get_winner(self):
        return self.game_state.winner


async def join_game(websocket: WebSocket, token: str, db: Session):
    connection_id = await connectionManager.connect(websocket)
    user = await get_current_user(token, db)
    user_connection = schemas.UserConnection(
        connection_id=connection_id, **user.model_dump()
    )

    connected = False

    async def check_connected() -> Tuple[None | str, bool]:
        result = (None, False)
        try:
            while not connected:
                result = (await websocket.receive_text(), False)
        except WebSocketDisconnect:
            result = (None, True)
        finally:
            return result

    async def get_find_match() -> Tuple[None | Game, bool]:
        return await matchmaker.find_game(user_connection), False

    await websocket.send_json(
        {
            "status": "waiting",
            "connection_id": str(connection_id),
        }
    )

    task1 = check_connected()
    task2 = get_find_match()

    done, pending = await asyncio.wait(
        [task1, task2], return_when=asyncio.FIRST_COMPLETED
    )
    done_task = done.pop()
    result, connection_closed = done_task.result()

    pending_task = pending.pop()

    if connection_closed:
        print(f"{connection_id} disconnected")
        connectionManager.disconnect(connection_id)
        return

    if (game := result) is not None:
        game.join(user_connection)
        connected = True

        try:
            move, _ = await pending_task

            while game.get_winner() is None and move is not None:
                await game.push_move(user_connection, move)
                move = await websocket.receive_text()


        except (WebSocketDisconnect, RuntimeError):
            pass

        print(f"{connection_id} disconnected")
        await game.disconnect(connection_id)
        connectionManager.disconnect(connection_id)


connectionManager = ConnectionManager()
matchmaker = Matchmaker()
