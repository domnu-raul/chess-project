import asyncio, threading, bisect
from typing import List, Tuple

from src.database import schemas
from src.utils.game import Game

__waiting_queue: List[Tuple[schemas.UserConnection, asyncio.Queue]] = list[Tuple[schemas.UserConnection, asyncio.Queue]]()
__MATCHMAKING_RANGE = 100

def __add(user: schemas.UserConnection):
    queue = asyncio.Queue()
    bisect.insort(
        __waiting_queue, (user,
                                queue), key=lambda o: o[0].details.elo_rating
    )

    return queue

def __matchmaking():
    while True:
        if len(__waiting_queue) >= 2:
            for i in range(0, len(__waiting_queue) - 1):
                player_a, queue_a = __waiting_queue[i]
                player_b, queue_b = __waiting_queue[i + 1]
                if (
                    abs(player_a.details.elo_rating -
                        player_b.details.elo_rating)
                    <= __MATCHMAKING_RANGE
                ):
                    __waiting_queue.pop(i)
                    __waiting_queue.pop(i)

                    game = Game()
                    queue_a.put_nowait(game)
                    queue_b.put_nowait(game)

async def find_game(user: schemas.UserConnection):
    queue = __add(user)

    game = await queue.get()
    return game

threading.Thread(target=__matchmaking, daemon=True).start()
