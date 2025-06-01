# # from fastapi import FastAPI
# # from api.v1 import users, playlists

# # app = FastAPI()
# # app.include_router(users.router)
# # app.include_router(playlists.router)

# '''

#     #
#     #   Пример для оптимизированного вызова grpc
#     #

#     # В FastAPI роутере 
#     from fastapi import Depends

#     async def get_user_stub():
#         channel = get_user_channel()
#         return commands_pb2_grpc.UserCommandServiceStub(channel)

#     from fastapi import FastAPI
#     from core.middleware.logging import log_requests
#     from core.logger import setup_logging

#     app = FastAPI()
#     setup_logging(settings.LOKI_URL)  # LOKI_URL из env-переменных

#     # Подключение middleware
#     app.middleware("http")(log_requests)


        
#     @router.post("/register")
#     async def register(
#         stub: UserCommandServiceStub = Depends(get_user_stub)
#     ):
#         await stub.RegisterUser(...)

# '''

# from src.services.user_service import register_user
# from src.core.middleware.auth import AuthMiddleware
# import random


# from fastapi import FastAPI
# from src.core.container import Container
# from src.api.v1.auth import router as auth_router
# from src.api.v1.users import router as users_router
# from src.api.v1.streaming import router as streaming_router
# import uvicorn

# app = FastAPI(title="API Gateway")
# container = Container()
# app.container = container
# app.include_router(auth_router)
# app.include_router(users_router)
# app.include_router(streaming_router)
# # app.add_middleware(AuthMiddleware)


# if __name__ == "__main__":

#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=8000,
#         log_level="info",
#         access_log=True,
#         reload=True,
#     )

# # if __name__ == "__main__":
# #     user_id = register_user(
# #         username=f"{random.randint(1, 10**10)}",
# #         email=f"john@example.com{random.randint(1, 10**10)}",
# #         password="secure123"
# #     )
# #     print(f"Registered user ID: {user_id}")

import asyncio
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.websockets import WebSocketState
import grpc
from pydantic import BaseModel
import src.protos.streaming_context.generated.streaming_pb2 as pb2  # замените на ваш сгенерированный модуль
import src.protos.streaming_context.generated.streaming_pb2_grpc as pb2_grpc  # замените на ваш сгенерированный модуль

app = FastAPI()
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def get_player(request: Request):
    return templates.TemplateResponse("player.html", {"request": request})

# Хранилище состояния
class SessionState:
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}  # session_id -> session_data
        self.chunk_queues: Dict[str, asyncio.Queue] = {}  # session_id -> queue of chunks
        self.websockets: Dict[str, WebSocket] = {}  # session_id -> websocket

session_state = SessionState()

# gRPC клиент
class GRPCAudioClient:
    def __init__(self):
        self.channel = grpc.aio.insecure_channel('localhost:50056')  # замените на ваш адрес
        self.stub = pb2_grpc.StreamingServiceStub(self.channel)
        self.stream = None
    
    def _parse_session_info(self, session_info):
        # Для повторяющихся полей используем list comprehension
        available_bitrates = [bitrate for bitrate in session_info.available_bitrates]
        
        return {
            "session_id": session_info.session_id,
            "current_bitrate": session_info.current_bitrate,
            "available_bitrates": available_bitrates,
            "current_chunk": session_info.current_chunk,
            "chunk_size": session_info.chunk_size,
            "total_chunks": session_info.total_chunks,
            "status": pb2.SessionInfo.Status.Name(session_info.status)
        }

    async def start_stream(self, track_id: str, user_id: str, bitrate: str, session_id: Optional[str] = None):
        start_msg = pb2.ClientMessage(
            start=pb2.StartStream(
                track_id=track_id,
                user_id=user_id,
                bitrate=bitrate,
                session_id=session_id
            )
        )
        
        self.stream = self.stub.StreamAudio()
        await self.stream.write(start_msg)
        
        # Получаем первый ответ (SessionInfo)
        response = await self.stream.read()
        if response == grpc.aio.EOF:
            raise Exception("Stream closed by server")

        if not response.HasField('session'):
            raise Exception("Expected SessionInfo as first response")
        response = self._parse_session_info(response.session)
        return response
    
    async def control_stream(self, action: str, bitrate: Optional[str] = None, chunk_num: Optional[int] = None):
        if not self.stream:
            raise Exception("Stream not started")
        
        action_enum = pb2.StreamControl.Action.Value(action.upper())
        control_msg = pb2.ClientMessage(
            control=pb2.StreamControl(
                action=action_enum,
                bitrate=bitrate,
                chunk_num=chunk_num
            )
        )
        
        await self.stream.write(control_msg)
        
        # Ожидаем ответ (SessionInfo)
        response = await self.stream.read()


        if response == grpc.aio.EOF:
            raise Exception("Stream closed by server")

        if not response.HasField('session'):
            raise Exception("Expected SessionInfo after control")
        
        response = self._parse_session_info(response.session)
        print(f"New session's state received {response}")
        return response    
    async def send_ack(self, received_count: int):
        if not self.stream:
            raise Exception("Stream not started")
        
        ack_msg = pb2.ClientMessage(ack=pb2.ChunkAck(received_count=received_count))
        await self.stream.write(ack_msg)
    
    async def receive_chunks(self, session_id: str):
        try:
            while True:
                response = await self.stream.read()

                if response == grpc.aio.EOF:
                    print("Stream closed by server")
                    break

                if response.HasField('chunk'):
                    chunk = response.chunk
                    if session_id in session_state.chunk_queues:
                        await session_state.chunk_queues[session_id].put(chunk)
                    if chunk.is_last:
                        del session_state.active_sessions[session_id]
                        del session_state.chunk_queues[session_id]
                        break

        except Exception as e:
            print(f"Error receiving chunks: {e}")
            # Очистка состояния при ошибке
            if session_id in session_state.active_sessions:
                del session_state.active_sessions[session_id]
            if session_id in session_state.chunk_queues:
                del session_state.chunk_queues[session_id]

grpc_client = GRPCAudioClient()

# Модели для FastAPI
class StartStreamRequest(BaseModel):
    track_id: str
    user_id: str
    bitrate: str
    session_id: Optional[str] = None

class ControlStreamRequest(BaseModel):
    action: str  # "PAUSE", "RESUME", "STOP", "CHANGE_BITRATE", "SEEK"
    bitrate: Optional[str] = None
    chunk_num: Optional[int] = None

# WebSocket endpoint для получения чанков
@app.websocket("/ws/{session_id}")
async def websocket_chunks(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    if session_id not in session_state.active_sessions:
        await websocket.close(code=1008, reason="Session not found")
        return
    
    session_state.websockets[session_id] = websocket
    
    try:
        ack_counter = 0  # Счетчик чанков
        last_chunk_number = 0  # Номер последнего чанка
        
        while True:
            chunk = await session_state.chunk_queues[session_id].get()
            # await websocket.send_bytes(chunk.data)
            await websocket.send_text(str(chunk.number))

            ack_counter += 1
            last_chunk_number = chunk.number
            
            # Отправляем подтверждение каждые 10 чанков
            if ack_counter >= 10:
                print(f"Sent ack for last {ack_counter} chunks")
                await grpc_client.send_ack(ack_counter)
                ack_counter = 0  # Сбрасываем счетчик
                
    except WebSocketDisconnect:
        print(f"{ack_counter} chunk remaining unacked")
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # Отправляем подтверждение для оставшихся чанков при закрытии
        if ack_counter > 0:
            print(f"Sent ack for last {ack_counter} chunks")
            await grpc_client.send_ack(ack_counter)
        
        if session_id in session_state.websockets:
            del session_state.websockets[session_id]

# HTTP endpoint для старта сессии
@app.post("/start_stream")
async def start_stream(request: StartStreamRequest):
    try:
        session_data = await grpc_client.start_stream(
            request.track_id,
            request.user_id,
            request.bitrate,
            request.session_id
        )
        
        session_id = session_data["session_id"]
        session_state.active_sessions[session_id] = {
            "info": session_data,
            "client": grpc_client
        }
        session_state.chunk_queues[session_id] = asyncio.Queue()
        
        # Запускаем фоновую задачу для получения чанков
        asyncio.create_task(grpc_client.receive_chunks(session_id))
        
        return session_data  # Теперь возвращает нормализованный словарь
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# HTTP endpoint для управления сессией
@app.post("/control_stream/{session_id}")
async def control_stream(session_id: str, request: ControlStreamRequest):
    if session_id not in session_state.active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session_info = await grpc_client.control_stream(
            request.action,
            request.bitrate,
            request.chunk_num
        )
        
        # Обновляем информацию о сессии
        session_state.active_sessions[session_id]["info"] = session_info
        
        return {
            "current_bitrate": session_info.current_bitrate,
            "status": pb2.SessionInfo.Status.Name(session_info.status),
            "current_chunk": session_info.current_chunk
        }
    except Exception as e:
        # raise HTTPException(status_code=500, detail=str(e))
        raise 

# HTTP endpoint для получения информации о сессии
@app.get("/session_info/{session_id}")
async def get_session_info(session_id: str):
    if session_id not in session_state.active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_info = session_state.active_sessions[session_id]["info"]
    return {
        "current_bitrate": session_info.current_bitrate,
        "available_bitrates": session_info.available_bitrates,
        "status": pb2.SessionInfo.Status.Name(session_info.status),
        "current_chunk": session_info.current_chunk,
        "chunk_size": session_info.chunk_size,
        "total_chunks": session_info.total_chunks
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    )