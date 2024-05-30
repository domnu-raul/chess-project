import asyncio
from typing import Dict, List, Tuple, Optional
from uuid import UUID, uuid4
from fastapi import WebSocket, WebSocketDisconnect

from src.database import crud, get_db, schemas

connections: Dict[UUID, WebSocket] = dict[UUID, WebSocket]()

async def connect(websocket: WebSocket) -> UUID:
    connection_id = uuid4()

    await websocket.accept()

    connections[connection_id] = websocket

    return connection_id

def disconnect(connection_id: UUID) -> None:
    connections.pop(connection_id)

async def send_message_to(connection_id: UUID, message: str):
    await connections[connection_id].send_text(message)

async def send_json_to( connection_id: UUID, json: dict):
    try:
        await connections[connection_id].send_json(json)
    except (KeyError, RuntimeError):
        print(f"Connection {connection_id} not found")
