import asyncio
import grpc
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from src.protos.streaming_context.generated import streaming_pb2, streaming_pb2_grpc

app = FastAPI()

class GRPCAudioClient:
    def __init__(self, grpc_channel):
        self.stub = streaming_pb2_grpc.StreamingServiceStub(grpc_channel)
        self.session_id = None
        self._stream = None

    async def start_stream(self, track_id: str, user_id: str, bitrate: str):
        """Инициализация стрима"""
        start_msg = streaming_pb2.ClientMessage(
            start=streaming_pb2.StartStream(
                track_id=track_id,
                user_id=user_id,
                bitrate=bitrate
            )
        )
        self._stream = self.stub.StreamAudio(self._message_generator())
        await self._stream.write(start_msg)
        return self._stream

    async def _message_generator(self):
        """Генератор сообщений для gRPC стрима"""
        try:
            while True:
                msg = await self._control_queue.get()
                yield msg
        except asyncio.CancelledError:
            pass

    async def send_control(self, action: str, bitrate: str = None, chunk_num: int = None):
        """Отправка управляющего сообщения"""
        action_enum = getattr(streaming_pb2.StreamControl.Action, action.upper())
        control_msg = streaming_pb2.ClientMessage(
            control=streaming_pb2.StreamControl(
                action=action_enum,
                bitrate=bitrate,
                chunk_num=chunk_num
            )
        )
        await self._stream.write(control_msg)