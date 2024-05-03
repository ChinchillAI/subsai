from starlette.applications import Starlette
from starlette.endpoints import WebSocketEndpoint
from starlette.routing import WebSocketRoute

from typing import Literal
from pydantic import BaseModel, Field

class SubscribeCommand(BaseModel):
    command_type: Literal['subscribe']
    stream_id: int

class MessageCommand(BaseModel):
    command_type: Literal['message']
    stream_id: int
    message: str

class Command(BaseModel):
    command: SubscribeCommand | MessageCommand = Field(..., discriminator='command_type')

class ErrorResponse(BaseModel):
    response_type: Literal['error'] = 'error'
    message: str

class MessageResponse(BaseModel):
    response_type: Literal['message'] = 'message'
    stream_id: int
    message: str

class SubscribeResponse(BaseModel):
    response_type: Literal['subscribe'] = 'subscribe'
    subscriptions: str

class WebsocketTest(WebSocketEndpoint):
    encoding = "json"
    websocket_streams = {}
    stream_websockets = {}

    async def on_connect(self, websocket):
        await websocket.accept()
        self.websocket_streams[websocket] = set()

    async def on_receive(self, websocket, data):
        c = Command(command=data)
        match c.command:
            case SubscribeCommand(command_type=command_type, stream_id=stream_id):
                if c.command.stream_id not in self.stream_websockets.keys():
                    await websocket.send_json(ErrorResponse(message="stream does not exist").json())
                else:
                    self.websocket_streams[websocket].add(c.command.stream_id)
                    self.stream_websockets[c.command.stream_id].add(websocket)
                    await websocket.send_json(
                        SubscribeResponse(
                            subscriptions=str(self.websocket_streams[websocket])
                        ).json()
                    )
            case MessageCommand(command_type=command_type, stream_id=stream_id, message=message):
                if c.command.stream_id not in self.stream_websockets.keys():
                    self.stream_websockets[c.command.stream_id] = set()
                    self.stream_websockets[c.command.stream_id].add(websocket)
                    self.websocket_streams[websocket].add(c.command.stream_id)
                for subscriber in self.stream_websockets[stream_id]:
                    await subscriber.send_json(
                        MessageResponse(
                            stream_id=c.command.stream_id,
                            message=c.command.message
                        ).json()
                    )
            case other:
                await websocket.send_json(
                    ErrorResponse(message="bad websocket command").json()
                )

    async def on_disconnect(self, websocket, close_code):
        for stream in self.websocket_streams[websocket]:
            self.stream_websockets[stream].remove(websocket)
        del self.websocket_streams[websocket]


routes = [
    WebSocketRoute("/ws", WebsocketTest)
]

app = Starlette(routes=routes)