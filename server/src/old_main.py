from dataclasses import dataclass
import uuid

import chess
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio, multiprocessing

app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@dataclass
class Connection:
    _id : str
    ws : WebSocket

@dataclass
class ConnectionManager:
    active_connections : dict[str, WebSocket]
    waiting_connections : list[(multiprocessing.Pipe, WebSocket)]

    def __init__(self):
        self.active_connections = dict()
        self.waiting_connections = list()

    async def connect(self, _id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[_id] = websocket
        
    async def disconnect(self, connection_id: str):
        pass
    
    async def enter_queue(self, _id : str):
        websocket = self.active_connections[_id]
        pipe = multiprocessing.Pipe(duplex=False)
        self.waiting_connections.append((pipe, websocket))

        read, _ = pipe
        await websocket.send_text("Waiting...")

        while not read.poll():
            await asyncio.sleep(1)
        
        game_key = read.recv()
        await websocket.send_text(f"Match found! Game key: {game_key}")

    async def matchmaking(self):
        while True:
            if len(self.waiting_connections) >= 2:
                (pipe1, ws1), (pipe2, ws2) = self.waiting_connections.pop(0), self.waiting_connections.pop(0)

                game_key = str(uuid.uuid4())
                _, write1 = pipe1
                _, write2 = pipe2

                write1.send(game_key)
                write2.send(game_key)

@dataclass
class Game:
    board : chess.Board
    black_id : str
    white_id : str
    turn : str = "W"

    def move(player_id : str, move : str):
        pass

boards = dict()
games = dict()
connectionManager = ConnectionManager()

@app.post("/start")
async def start():
    board = chess.Board()
    game_key = str(uuid.uuid4())
    boards[game_key] = board

    return {"key": game_key, "fen": board.fen().split(" ")[0]}

@app.websocket("/play")
async def play(websocket : WebSocket):
    connection_id = str(uuid.uuid4())
    print(f"Connection ID: {connection_id}")
    await connectionManager.connect(connection_id, websocket)
    await connectionManager.enter_queue(connection_id)

    await connectionManager.disconnect(connection_id)


@app.get("/{game_key}")
async def get_move_tree(game_key: str):
    board = boards[game_key]
    moves = list(map(lambda m: m.uci(), board.legal_moves))
    starters = list(set(map(lambda m: m[:2], moves)))

    return {
        "moveTree": {
            starter: list(map(lambda m: m[2:], filter(lambda n: n[:2] == starter, moves)))
            for starter in sorted(starters)
        },
        "fen": board.fen().split(" ")[0],
    }


@app.put("/{game_key}/{uci_move}")
async def move(game_key: str, uci_move: str):
    board = boards[game_key]
    if uci_move in map(lambda m: m.uci(), board.legal_moves):
        board.push_uci(uci_move)

        return {"status": "success", "fen": board.fen().split(" ")[0]}
    else:
        return {"status": "invalid"}
