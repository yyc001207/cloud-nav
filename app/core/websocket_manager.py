import json
from fastapi import WebSocket
from typing import List, Dict


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {
            "strm_logs": [],
            "strm_error": [],
            "all": [],
        }

    async def connect(self, websocket: WebSocket, channel: str = "all"):
        await websocket.accept()
        if channel not in self.active_connections:
            channel = "all"
        self.active_connections[channel].append(websocket)

    def disconnect(self, websocket: WebSocket, channel: str = "all"):
        if channel in self.active_connections:
            if websocket in self.active_connections[channel]:
                self.active_connections[channel].remove(websocket)

    async def broadcast(self, message: dict, channel: str = "all"):
        if channel not in self.active_connections:
            channel = "all"
        disconnected = []
        for connection in self.active_connections[channel]:
            try:
                await connection.send_text(json.dumps(message, ensure_ascii=False))
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn, channel)


manager = ConnectionManager()


async def broadcast_log(log_data: dict):
    await manager.broadcast(log_data, "all")
