from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: int):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: int):
        del self.active_connections[client_id]

    async def send_personal_message(self, message: str, receiver_id: int):
        if receiver_id in self.active_connections:
            await self.active_connections[receiver_id].send_text(message)


manager = ConnectionManager()


@router.websocket('/chat/{client_id}')
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket, client_id)
    try:

        while True:
            data = await websocket.receive_text()
            received_id, message = data.split(':', 1)
            await manager.send_personal_message(message, int(received_id))

    except WebSocketDisconnect:
        manager.disconnect(client_id=client_id)

