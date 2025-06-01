from fastapi import APIRouter, Depends, HTTPException, status, WebSocket
from dependency_injector.wiring import inject, Provide
from src.core.jwt_utils import create_access_token, verify_token
from src.core.container import Container
from src.services.user_service import register_user, authenticate_user
from src.schemas.user import RegisterUserRequest, RegisterUserResponse, LoginUserRequest, LoginUserResponse
import grpc
from typing import Optional

from src.services.client import GRPCAudioClient


router = APIRouter(prefix="/streaming", tags=["Streaming"])

@router.websocket("/ws/audio/{track_id}")
async def websocket_audio_stream(websocket: WebSocket, track_id: str):
    await websocket.accept()
    
    # Подключаемся к gRPC серверу
    async with grpc.aio.insecure_channel('localhost:50056') as channel:
        client = GRPCAudioClient(channel)
        
        try:
            # Инициализация стрима
            user_id = "1"  # Должно приходить из аутентификации
            stream = await client.start_stream(track_id, user_id, "320")
            
            async for response in stream:
                if response.HasField("session"):
                    # Отправляем информацию о сессии клиенту
                    await websocket.send_json({
                        "type": "session_info",
                        "data": {
                            "session_id": response.session.session_id,
                            "bitrate": response.session.current_bitrate,
                            "status": response.session.status.name
                        }
                    })
                elif response.HasField("chunk"):
                    # Отправляем аудио-чанк
                    await websocket.send_bytes(response.chunk.data)
                    
                    # Подтверждение получения
                    ack = streaming_pb2.ClientMessage(
                        ack=streaming_pb2.ChunkAck(
                            received_count=response.chunk.number
                        )
                    )
                    await stream.write(ack)
                    
        except WebSocketDisconnect:
            print("Client disconnected")
        except Exception as e:
            print(f"Error: {str(e)}")
        finally:
            await websocket.close()

@router.post("/control/{session_id}")
async def control_stream(
    session_id: str,
    action: str,
    bitrate: Optional[str] = None,
    chunk_num: Optional[int] = None
):
    """Управление существующим стримом"""
    async with grpc.aio.insecure_channel('grpc-server:50051') as channel:
        client = GRPCAudioClient(channel)
        await client.send_control(action, bitrate, chunk_num)
        return {"status": "control_sent"}
