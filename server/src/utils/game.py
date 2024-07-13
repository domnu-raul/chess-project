from uuid import UUID, uuid4
import chess
import asyncio
import threading
from typing import Optional, Tuple
from src.database import models, schemas
from sqlalchemy.orm import Session

from src.database import crud
from src.database import get_db
from src.utils import connection_manager

_db_object = next(get_db())
game_map = {}


class Game:
    board: chess.Board
    black: Optional[schemas.UserConnection] = None
    white: Optional[schemas.UserConnection] = None
    game_state: Optional[schemas.GameState] = None
    pushed_move: Optional[Tuple[schemas.UserConnection, str]] = None
    pushed_message: Optional[Tuple[schemas.UserConnection, str]] = None

    @property
    def winner(self):
        return self.game_state.winner

    def __init__(self):
        def run_in_new_loop(loop, coro):
            asyncio.set_event_loop(loop)
            loop.run_until_complete(coro)
            loop.close()

        self.board = chess.Board()
        self.game_state = schemas.GameState(fen=self.board.fen())

        new_loop = asyncio.new_event_loop()
        threading.Thread(
            target=run_in_new_loop, args=(new_loop, self.engine()), daemon=True
        ).start()

    def new_hashed() -> UUID:
        game = Game()
        game_id = uuid4()
        game_map[game_id] = game
        return game_id

    def get_hashed(game_id: UUID) -> "Game":
        return game_map[game_id]

    def join(self, player: schemas.UserConnection):
        if self.white is None:
            self.white = player
        elif self.black is None:
            self.black = player
        else:
            raise Exception("Game is full")

    async def disconnect(self, player: schemas.UserConnection):
        self.game_state.is_end = True
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
            self.__get_game_update_for_player(self.white, True).model_dump()
        )

        await connection_manager.send_json_to(
            self.black.connection_id,
            self.__get_game_update_for_player(self.black, True).model_dump()
        )

        while not self.game_state.is_end:
            if (t := self.pushed_message) is not None:
                player, msg = t
                other_player = self.white if player == self.black else self.black

                response = schemas.GameResponse(
                    success=True,
                    type='CHAT',
                    content=schemas.ChatUpdate(
                        sender_id=player.id, message=msg)
                )

                await connection_manager.send_json_to(
                    other_player.connection_id,
                    response.model_dump(),
                )

                await connection_manager.send_json_to(
                    player.connection_id,
                    response.model_dump(),
                )

                self.pushed_message = None

            if (t := self.pushed_move) is not None:
                player, move = t
                self.board.push(chess.Move.from_uci(move))

                self.__update_state(last_move=move)
                self.pushed_move = None

                other_player = self.white if player == self.black else self.black
                response = self.__get_game_update_for_player(player, True)
                response_other = self.__get_game_update_for_player(
                    other_player, True)

                await connection_manager.send_json_to(
                    other_player.connection_id,
                    response_other.model_dump(),
                )

                await connection_manager.send_json_to(
                    player.connection_id,
                    response.model_dump(),
                )

        final_state_white = self.__get_game_update_for_player(self.white, True)
        final_state_black = self.__get_game_update_for_player(self.black, True)
        final_state_white.content.legal_moves = []
        final_state_black.content.legal_moves = []

        await connection_manager.send_json_to(self.black.connection_id, final_state_black.model_dump())
        await connection_manager.send_json_to(self.white.connection_id, final_state_white.model_dump())

        self.__end_game()
        await self.disconnect(self.white)
        await self.disconnect(self.black)

    async def push_msg(self, player: schemas.UserConnection, msg: str):
        args = msg.split(":", maxsplit=1)
        command = args[0].strip().upper()
        option = ""
        if len(args) > 1:
            option = args[1].strip()
        match command:
            case "MOVE":
                await self.__push_move(player, option)
            case "CHAT":
                await self.__push_chat_msg(player, option)
            case "RESIGN":
                self.game_state.is_end = True
                self.game_state.winner = "W" if player == self.black else "B"
                response = self.__get_game_update_for_player(player, False)

                await connection_manager.send_json_to(
                    player.connection_id,
                    response.model_dump(),
                )
            case _:
                response = self.__get_game_update_for_player(player, False)

                await connection_manager.send_json_to(
                    player.connection_id,
                    response.model_dump(),
                )

    async def __push_move(self, player: schemas.UserConnection, move: str):
        if self.__is_valid_move(move) and self.__is_player_turn(player):
            self.pushed_move = (player, move)
        else:
            response = self.__get_game_update_for_player(player, False)

            await connection_manager.send_json_to(
                player.connection_id,
                response.model_dump(),
            )

    async def __push_chat_msg(self, player: schemas.UserConnection, msg: str):
        self.pushed_message = (player, msg)

    def __get_game_update_for_player(self, player: schemas.UserConnection, success: bool):
        response = schemas.GameResponse(
            success=success,
            type='GAME_UPDATE',
            content=schemas.GameUpdate(
                **self.__get_state_for_player(player).model_dump(),
                color="W" if player == self.white else "B",
                white_player_id=self.white.id,
                black_player_id=self.black.id,
            )
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

        self.game_state.turn = "W" if self.board.turn == chess.WHITE else "B"
        self.game_state.fen = self.board.fen()
        self.game_state.last_move = last_move
        self.game_state.legal_moves = moves

    def __end_game(self):
        white_player, black_player = self.__get_game_players()
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

            white_player.game_id = game_object.game_id
            black_player.game_id = game_object.game_id

            crud.create_game_player(white_player, game_object, _db_object)
            crud.create_game_player(black_player, game_object, _db_object)

    def __get_game_players(self):
        def expected_score(a, b): return 1 / (1 + 10 ** ((b - a) / 400))

        outcome_w = 1 if self.winner == "W" else 0.5 if self.winner is None else 0

        outcome_b = 1 - outcome_w

        expected_w = expected_score(
            self.white.details.elo_rating, self.black.details.elo_rating)
        expected_b = expected_score(
            self.black.details.elo_rating, self.white.details.elo_rating)

        gained_elo_w = round(32 * (outcome_w - expected_w))
        gained_elo_b = round(32 * (outcome_b - expected_b))

        white_player = schemas.GamePlayer(
            game_id=None, player_id=self.white.id, gained_elo=gained_elo_w)

        black_player = schemas.GamePlayer(
            game_id=None, player_id=self.black.id, gained_elo=gained_elo_b)

        return white_player, black_player
