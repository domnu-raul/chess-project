import uuid

import chess
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

boards = dict()


@app.post("/start")
async def start():
    board = chess.Board()
    game_key = str(uuid.uuid4())
    boards[game_key] = board

    return {"key": game_key, "fen": board.fen().split(" ")[0]}


@app.get("/{game_key}")
async def get_move_tree(game_key: str):
    board = boards[game_key]
    moves = list(map(lambda m: m.uci(), board.legal_moves))
    starters = list(set(map(lambda m: m[:2], moves)))

    return {
        starter: list(map(lambda m: m[2:], filter(lambda n: n[:2] == starter, moves)))
        for starter in sorted(starters)
    }


@app.put("/{game_key}/{uci_move}")
async def move(game_key: str, uci_move: str):
    board = boards[game_key]
    if uci_move in map(lambda m: m.uci(), board.legal_moves):
        board.push_uci(uci_move)

        return {"status": "success", "fen": board.fen().split(" ")[0]}
    else:
        return {"status": "invalid"}
