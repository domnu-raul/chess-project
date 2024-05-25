from typing import Annotated, Tuple, List, Dict
import asyncio
import threading
import chess

from dataclasses import dataclass
from uuid import UUID, uuid4

from services.auth_service import get_current_user
from sqlalchemy.orm import Session

from fastapi import WebSocket, WebSocketDisconnect

from database import schemas


# TODO make a connection class(ws and user)
# TODO move game logic to a Game class
# TODO move ConnectionManager to a separate file
# TODO optimise game state updates, make a class for game state
# TODO add game state to Game class
# TODO add update_state method to Game class
# TODO add an event loop to Game class
# TODO implement ELO and matchmaking(maybe use a separate service for that)

# TODO add ELO rating to User model, also wins/losses/draws
# TODO create a table for game history
# TODO handle promotions


@dataclass
class ConnectionManager:
    active_connections: Dict[UUID, Tuple[WebSocket, schemas.User]]
    waiting_connections: Dict[UUID, asyncio.Queue]

    def __init__(self):
        self.active_connections = dict()
        self.waiting_connections = dict()

        threading.Thread(target=self.matchmaking, daemon=True).start()

    async def connect(self, websocket: WebSocket) -> UUID:
        connection_id = uuid4()

        await websocket.accept()

        self.active_connections[connection_id] = websocket
        return connection_id

    def disconnect(self, connection_id: UUID) -> None:
        self.active_connections.pop(connection_id)
        self.waiting_connections.pop(connection_id)

    async def find_match(self, connection_id: UUID):
        queue = asyncio.Queue()

        self.waiting_connections[connection_id] = queue

        game = await queue.get()
        return game

    def matchmaking(self):
        while True:
            if len(self.waiting_connections) >= 2:
                _, q1 = self.waiting_connections.popitem()
                _, q2 = self.waiting_connections.popitem()

                game = Game()

                q1.put_nowait(game)
                q2.put_nowait(game)

    async def send_message_to(self, connection_id: UUID, message: str):
        await self.active_connections[connection_id].send_text(message)

    async def send_json_to(self, connection_id: UUID, json: dict):
        await self.active_connections[connection_id].send_json(json)


@dataclass
class Player:
    connection_id: UUID
    user: schemas.User


@dataclass
class Game:
    black: Player
    white: Player
    board: chess.Board
    winner: UUID | None = None

    def __init__(self):
        self.board = chess.Board()
        self.white = None
        self.black = None

    def join(self, player: Player):
        if self.white is None:
            self.white = player
        elif self.black is None:
            self.black = player
        else:
            raise Exception("Game is full")

        # TODO return game status message to player

    async def move(self, player: Player, move: str):
        valid = False

        try:
            uci_move = chess.Move.from_uci(move)

            if player is self.white and self.board.turn == chess.WHITE:
                if self.board.is_legal(uci_move):
                    self.board.push(uci_move)
                    valid = True

            elif player is self.black and self.board.turn == chess.BLACK:
                if self.board.is_legal(uci_move):
                    self.board.push(uci_move)
                    valid = True

        except chess.InvalidMoveError:
            pass

        if (outcome := self.board.outcome()) is not None:
            self.winner = (
                "W"
                if outcome.winner == chess.WHITE
                else "B" if outcome.winner == chess.BLACK else "D"
            )

        moves = [move.uci() for move in self.board.legal_moves]
        starters = list(set(map(lambda m: m[:2], moves)))

        move_tree = {
            starter: list(
                map(lambda m: m[2:], filter(lambda n: n[:2] == starter, moves))
            )
            for starter in sorted(starters)
        }

        white_move_tree = move_tree if self.board.turn == chess.WHITE else {}
        black_move_tree = move_tree if self.board.turn == chess.BLACK else {}

        output = {
            "status": "success",
            "fen": self.get_fen(),
            "turn": "W" if self.board.turn == chess.WHITE else "B",
            "winner": self.get_winner(),
        }

        if valid:
            output["last_move"] = move
            output["move_tree"] = white_move_tree
            await connectionManager.send_json_to(self.white.connection_id, output)

            output["move_tree"] = black_move_tree
            await connectionManager.send_json_to(self.black.connection_id, output)
        else:
            output["status"] = "invalid"
            await connectionManager.send_json_to(player.connection_id, output)

    def get_fen(self):
        return self.board.fen()

    def get_winner(self):
        return self.winner

    def get_color(self, player):
        if player == self.white:
            return "W"
        elif player == self.black:
            return "B"
        else:
            return None

    async def disconnect(self, player: UUID):
        output = {"fen": self.get_fen(), "turn": "", "winner": ""}

        if player == self.white:
            self.winner = "B"
            output["winner"] = "B"
            await connectionManager.send_json_to(self.black.connection_id, output)
        else:
            self.winner = "W"
            output["winner"] = "W"
            await connectionManager.send_json_to(self.white.connection_id, output)


async def join_game(websocket: WebSocket, token: str, db: Session):
    user = await get_current_user(token, db)
    connection_id = await connectionManager.connect(websocket)
    player = Player(connection_id, user)

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
        return await connectionManager.find_match(connection_id), False

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
        game.join(player)
        connected = True

        await websocket.send_json(
            {
                "status": "success",
                "fen": game.get_fen(),
                "color": game.get_color(player),
            }
        )

        try:
            move, _ = await pending_task

            while game.get_winner() is None:
                await game.move(player, move)
                move = await websocket.receive_text()

        except (WebSocketDisconnect, RuntimeError):
            pass

        print(f"{connection_id} disconnected")
        await game.disconnect(connection_id)
        connectionManager.disconnect(connection_id)


connectionManager = ConnectionManager()
