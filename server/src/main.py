from dataclasses import dataclass
from uuid import UUID, uuid4

from fastapi import (
    Depends,
    FastAPI,
    WebSocket,
    Body,
    status,
)

from typing import Annotated, Tuple, List, Dict

import asyncio
import threading
import chess

from database import get_db, init_db
from sqlalchemy.orm import Session

from database.models import UserDB
from schemas.models import User, UserIn
from routers import auth

app = FastAPI()
init_db()

app.include_router(auth.router)


@dataclass
class ConnectionManager:
    active_connections: Dict[UUID, WebSocket]
    waiting_connections: List[Tuple[UUID, asyncio.Queue]]

    def __init__(self):
        self.active_connections = dict()
        self.waiting_connections = list()

        threading.Thread(target=self.matchmaking).start()

    async def connect(self, websocket: WebSocket) -> UUID:
        connection_id = uuid4()

        await websocket.accept()

        self.active_connections[connection_id] = websocket
        return connection_id

    async def disconnect(self, connection_id: UUID) -> None:
        await self.active_connections[connection_id].close()
        self.active_connections.pop(connection_id)

    async def find_match(self, connection_id: UUID):
        queue = asyncio.Queue()

        self.waiting_connections.append((connection_id, queue))

        game = await queue.get()

        return game

    def matchmaking(self):
        while True:
            if len(self.waiting_connections) >= 2:
                id1, q1 = self.waiting_connections.pop(0)
                id2, q2 = self.waiting_connections.pop(0)

                game = Game(id1, id2, chess.Board())

                q1.put_nowait(game)
                q2.put_nowait(game)

    async def send_message(self, connection_id: UUID, message: str):
        await self.active_connections[connection_id].send_text(message)

    async def send_json(self, connection_id: UUID, json: dict):
        await self.active_connections[connection_id].send_json(json)


@dataclass
class Game:
    black_id: UUID
    white_id: UUID
    board: chess.Board
    winner: UUID | None = None

    async def move(self, player: UUID, move: str):
        valid = False

        try:
            uci_move = chess.Move.from_uci(move)

            if player == self.white_id and self.board.turn == chess.WHITE:
                if self.board.is_legal(uci_move):
                    self.board.push(uci_move)
                    valid = True

            elif player == self.black_id and self.board.turn == chess.BLACK:
                if self.board.is_legal(uci_move):
                    self.board.push(uci_move)
                    valid = True

        except chess.InvalidMoveError:
            pass

        if self.board.is_checkmate():
            self.winner = player

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
            await connectionManager.send_json(self.white_id, output)

            output["move_tree"] = black_move_tree
            await connectionManager.send_json(self.black_id, output)
        else:
            output["status"] = "invalid"
            await connectionManager.send_json(player, output)

    def get_fen(self):
        return self.board.fen()

    def get_winner(self):
        return self.winner

    def get_color(self, player_id: UUID):
        if player_id == self.white_id:
            return "W"
        elif player_id == self.black_id:
            return "B"
        else:
            return None


connectionManager = ConnectionManager()


@app.websocket("/play")
async def play(websocket: WebSocket):
    connection_id = await connectionManager.connect(websocket)
    await websocket.send_text(f"Connected! Your ID: {connection_id}")

    game = await connectionManager.find_match(connection_id)

    await websocket.send_json(
        {
            "status": "success",
            "fen": game.get_fen(),
            "color": game.get_color(connection_id),
        }
    )

    while game.get_winner() is None:
        data = await websocket.receive_text()
        await game.move(connection_id, data)

    await connectionManager.disconnect(connection_id)
