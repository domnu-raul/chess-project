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

# TODO move ConnectionManager to a separate file

# TODO add a leaderboard endpoint

# TODO document the code


class ConnectionManager:
    connections: Dict[UUID, WebSocket]

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
            self.waiting_queue, (user,
                                 queue), key=lambda o: o[0].details.elo_rating
        )

        return queue

    def matchmaking(self):
        while True:
            if len(self.waiting_queue) >= 2:
                for i in range(0, len(self.waiting_queue) - 1):
                    player_a, queue_a = self.waiting_queue[i]
                    player_b, queue_b = self.waiting_queue[i + 1]
                    if (
                        abs(player_a.details.elo_rating -
                            player_b.details.elo_rating)
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


class Game:
    board: chess.Board
    black: Optional[schemas.UserConnection] = None
    white: Optional[schemas.UserConnection] = None
    game_state: Optional[schemas.GameState] = None
    pushed_move: Optional[Tuple[schemas.UserConnection, str]] = None

    def __init__(self):
        self.board = chess.Board()
        self.game_state = schemas.GameState(fen=self.board.fen())

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

    def __end_game(self):
        self.__update_player_data()

        game_model = schemas.Game(
            white_player_id=self.white.id,
            black_player_id=self.black.id,
            white_player=self.white,
            black_player=self.black,
            moves=[move.uci() for move in self.board.move_stack],
            winner=None if self.game_state.winner is None else self.white.id if self.game_state.winner == "W" else self.black.id,)

        if _db_object is not None:
            game_object = crud.create_game(
                game_model, _db_object)

    def __update_player_data(self):
        def expected_score(a, b): return 1 / (1 + 10 ** ((b - a) / 400))

        outcome_w = 1 if self.game_state.winner == "W" \
            else 0.5 if self.game_state.winner is None \
            else 0

        outcome_b = 1 - outcome_w

        expected_w = expected_score(
            self.white.details.elo_rating, self.black.details.elo_rating)
        expected_b = expected_score(
            self.black.details.elo_rating, self.white.details.elo_rating)

        new_rating_w = self.white.details.elo_rating + \
            32 * (outcome_w - expected_w)
        new_rating_b = self.black.details.elo_rating + \
            32 * (outcome_b - expected_b)

        self.white.details.elo_rating = round(new_rating_w)
        self.black.details.elo_rating = round(new_rating_b)

        if self.game_state.winner is None:
            self.white.details.draws += 1
            self.black.details.draws += 1
        elif self.game_state.winner == "W":
            self.white.details.wins += 1
            self.black.details.losses += 1
        else:
            self.white.details.losses += 1
            self.black.details.wins += 1

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

                response = self.__get_response_for_player(player, True)
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

        self.__end_game()

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
        moves = [move.uci() for move in self.board.legal_moves]

        outcome = self.board.outcome()
        if outcome is not None:
            self.game_state.is_end = True
            self.game_state.winner = (
                "W"
                if outcome.winner == chess.WHITE
                else "B" if outcome.winner == chess.BLACK else None
            )

        self.game_state.player_turn = "W" if self.board.turn == chess.WHITE else "B"
        self.game_state.fen = self.board.fen()
        self.game_state.last_move = last_move
        self.game_state.legal_moves = moves

    async def disconnect(self, player: schemas.UserConnection):
        if player is self.white:
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
        except (WebSocketDisconnect, RuntimeError) as e:
            pass

        print(f"{connection_id} disconnected")
        await game.disconnect(user_connection)
        connectionManager.disconnect(connection_id)


connectionManager = ConnectionManager()
matchmaker = Matchmaker()
_db_object = next(get_db())
