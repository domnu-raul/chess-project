import chess, asyncio, threading
from typing import Optional, Tuple
from src.database import schemas
from sqlalchemy.orm import Session

from src.database import crud
from src.database import get_db
from src.utils import connection_manager

_db_object = next(get_db())

class Game:
    board: chess.Board
    black: Optional[schemas.UserConnection] = None
    white: Optional[schemas.UserConnection] = None
    game_state: Optional[schemas.GameState] = None
    pushed_move: Optional[Tuple[schemas.UserConnection, str]] = None

    @property
    def winner(self):
        return self.game_state.winner

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

    async def disconnect(self, player: schemas.UserConnection):
        if player is self.white:
            self.game_state.winner = "B"
        else:
            self.game_state.winner = "W"

    async def engine(self):
        while self.black is None or self.white is None:
            await asyncio.sleep(1)

        self.__update_state()

        await connection_manager.send_json_to(
            self.white.connection_id,
            dict(
                self.__get_response_for_player(self.white, True).model_dump(), color="W"
            ),
        )

        await connection_manager.send_json_to(
            self.black.connection_id,
            dict(
                self.__get_response_for_player(self.black, True).model_dump(), color="B"
            ),
        )

        while self.winner is None:
            if (t := self.pushed_move) is not None:
                player, move = t
                self.board.push(chess.Move.from_uci(move))

                self.__update_state(last_move=move)
                self.pushed_move = None

                response = self.__get_response_for_player(player, True)
                other_player = self.white if player == self.black else self.black

                await connection_manager.send_json_to(
                    other_player.connection_id,
                    self.__get_state_for_player(other_player).model_dump(),
                )

                await connection_manager.send_json_to(
                    player.connection_id,
                    response.model_dump(),
                )

        final_state = self.game_state.model_dump()

        await connection_manager.send_json_to(self.black.connection_id, final_state)
        await connection_manager.send_json_to(self.white.connection_id, final_state)

        self.__end_game()

    async def push_move(self, player: schemas.UserConnection, move: str):
        if self.__is_valid_move(move) and self.__is_player_turn(player):
            self.pushed_move = (player, move)
        else:
            response = self.__get_response_for_player(player, False)

            await connection_manager.send_json_to(
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
            self.game_state.winner = (
                "W"
                if outcome.winner == chess.WHITE
                else "B" if outcome.winner == chess.BLACK else None
            )

        self.game_state.player_turn = "W" if self.board.turn == chess.WHITE else "B"
        self.game_state.fen = self.board.fen()
        self.game_state.last_move = last_move
        self.game_state.legal_moves = moves

    def __end_game(self):
        self.__update_player_data()

        game_model = schemas.Game(
            white_player_id=self.white.id,
            black_player_id=self.black.id,
            white_player=self.white,
            black_player=self.black,
            moves=[move.uci() for move in self.board.move_stack],
            winner=None if self.winner is None else self.white.id if self.winner == "W" else self.black.id,)

        if _db_object is not None:
            game_object = crud.create_game(
                game_model, _db_object)

    def __update_player_data(self):
        def expected_score(a, b): return 1 / (1 + 10 ** ((b - a) / 400))

        outcome_w = 1 if self.winner == "W" \
            else 0.5 if self.winner is None \
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

        if self.winner is None:
            self.white.details.draws += 1
            self.black.details.draws += 1
        elif self.winner == "W":
            self.white.details.wins += 1
            self.black.details.losses += 1
        else:
            self.white.details.losses += 1
            self.black.details.wins += 1
