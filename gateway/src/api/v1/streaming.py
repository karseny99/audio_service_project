import asyncio
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi import APIRouter, Depends, status
from fastapi.websockets import WebSocketState
import grpc
from pydantic import BaseModel
import src.protos.streaming_context.generated.streaming_pb2 as pb2 
import src.protos.streaming_context.generated.streaming_pb2_grpc as pb2_grpc 

router = APIRouter(tags=["audio_streaming"])

class SessionState:
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}  # session_id -> session_data
        self.chunk_queues: Dict[str, asyncio.Queue] = {}  # session_id -> queue of chunks
        self.control_queues: Dict[str, asyncio.Queue] = {}  # session_id -> queue of controls
        self.websockets: Dict[str, WebSocket] = {}  # session_id -> websocket

session_state = SessionState()

# gRPC клиентclass GRPCAudioClient:
class GRPCAudioClient:
    def __init__(self):
        self.channel = grpc.aio.insecure_channel('localhost:50056')
        self.stub = pb2_grpc.StreamingServiceStub(self.channel)
        self.stream = None
        self._receive_task = None

    def _parse_session_info(self, session_info):
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

    async def _init_stream_connection(self):
        """Инициализация gRPC соединения"""
        if self.stream is None:
            self.stream = self.stub.StreamAudio()

    async def _start_background_receiver(self, session_id: str):
        """Запуск фоновой задачи для приема сообщений"""
        if session_id not in session_state.control_queues:
            session_state.control_queues[session_id] = asyncio.Queue()
        if session_id not in session_state.chunk_queues:
            session_state.chunk_queues[session_id] = asyncio.Queue()
        
        self._receive_task = asyncio.create_task(self._message_receiver(session_id))

    async def _message_receiver(self, session_id: str):
        """Фоновая задача для приема всех сообщений от сервера"""
        try:
            while True:
                response = await self.stream.read()
                
                if response == grpc.aio.EOF:
                    print("Stream closed by server")
                    break
                
                if response.HasField('chunk'):
                    await session_state.chunk_queues[session_id].put(response.chunk)
                    if response.chunk.is_last:
                        break
                
                elif response.HasField('session'):
                    parsed = self._parse_session_info(response.session)
                    await session_state.control_queues[session_id].put(parsed)
        except Exception as e:
            print(f"Error in message receiver: {e}")
        finally:
            await self._cleanup_session(session_id)

    async def _cleanup_session(self, session_id: str):
        """Очистка ресурсов сессии"""
        if session_id in session_state.active_sessions:
            del session_state.active_sessions[session_id]
        if session_id in session_state.chunk_queues:
            del session_state.chunk_queues[session_id]
        if session_id in session_state.control_queues:
            del session_state.control_queues[session_id]

    async def start_stream(self, track_id: str, user_id: str, bitrate: str, session_id: Optional[str] = None):
        """Основной метод для старта сессии"""
        await self._init_stream_connection()
        
        start_msg = pb2.ClientMessage(
            start=pb2.StartStream(
                track_id=track_id,
                user_id=user_id,
                bitrate=bitrate,
                session_id=session_id
            )
        )
        
        await self.stream.write(start_msg)
        
        # Ждем первый SessionInfo без фоновых обработчиков
        response = await self.stream.read()
        if response == grpc.aio.EOF:
            raise Exception("Stream closed by server")
        if not response.HasField('session'):
            raise Exception("Expected SessionInfo as first response")
        
        session_info = self._parse_session_info(response.session)
        session_id = session_info["session_id"]
        
        # Инициализируем сессию
        session_state.active_sessions[session_id] = {
            "info": session_info,
            "client": self
        }
        
        # Только после успешного старта запускаем фоновые обработчики
        await self._start_background_receiver(session_id)
        
        return session_info

    async def control_stream(self, action: str, bitrate: Optional[str] = None, chunk_num: Optional[int] = None):
        if not self.stream:
            raise Exception("Stream not started")
        
        session_id = next(iter(session_state.active_sessions), None)
        if not session_id:
            raise Exception("No active session")
        
        action_enum = pb2.StreamControl.Action.Value(action.upper())
        control_msg = pb2.ClientMessage(
            control=pb2.StreamControl(
                action=action_enum,
                bitrate=bitrate,
                chunk_num=chunk_num
            )
        )
        
        await self.stream.write(control_msg)
        
        if action.upper() in ("PAUSE", "RESUME"):
            current_session = session_state.active_sessions[session_id]["info"]
            
            if action.upper() == 'PAUSE':
                current_session['status'] = 'PAUSE'
            else:
                current_session['status'] = 'ACTIVE'

            return current_session

        try:
            return await asyncio.wait_for(
                session_state.control_queues[session_id].get(),
                timeout=5.0
            )
        except asyncio.TimeoutError:
            raise Exception("Timeout waiting for session update")

    async def send_ack(self, received_count: int):
        if not self.stream:
            raise Exception("Stream not started")
        
        ack_msg = pb2.ClientMessage(ack=pb2.ChunkAck(received_count=received_count))
        await self.stream.write(ack_msg)

    async def close(self):
        if self._receive_task:
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass
        
        if self.stream:
            await self.stream.done_writing()
        
        if self.channel:
            await self.channel.close()

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
@router.websocket("/ws/{session_id}")
async def websocket_chunks(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    if session_id not in session_state.active_sessions:
        await websocket.close(code=1008, reason="Session not found")
        return
    
    session_state.websockets[session_id] = websocket
    
    try:
        ack_counter = 0
        last_chunk_number = 0
        
        while True:
            # Получаем чанк из очереди
            chunk = await session_state.chunk_queues[session_id].get()
            await websocket.send_text(str(chunk.number))

            ack_counter += 1
            last_chunk_number = chunk.number
            
            # Отправляем подтверждение 
            if ack_counter >= 10:
                await session_state.active_sessions[session_id]["client"].send_ack(ack_counter)
                ack_counter = 0
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # Отправляем оставшиеся подтверждения
        if ack_counter > 0 and session_id in session_state.active_sessions:
            await session_state.active_sessions[session_id]["client"].send_ack(ack_counter)
            ack_counter = 0
        
        if session_id in session_state.websockets:
            del session_state.websockets[session_id]
        if session_id in session_state.active_sessions:
            del session_state.active_sessions[session_id]
        if session_id in session_state.chunk_queues:
            del session_state.chunk_queues[session_id]
        if session_id in session_state.control_queues:
            del session_state.control_queues[session_id]


# HTTP endpoint для старта сессии
@router.post("/start_stream")
async def start_stream(request: StartStreamRequest):
    try:
        # Инициализация клиента вынесена в отдельный middleware или в startup
        grpc_client = GRPCAudioClient()
        session_data = await grpc_client.start_stream(
            request.track_id,
            request.user_id,
            request.bitrate,
            request.session_id
        )
        
        session_id = session_data["session_id"]
        session_state.active_sessions[session_id] = {
            "info": session_data,
            "client": grpc_client  # Сохраняем клиент в сессии
        }
        
        # Очередь создается автоматически в _start_background_receiver
        # Фоновая задача уже запущена внутри start_stream
        
        return session_data
        
    except Exception as e:
        raise
        # raise HTTPException(status_code=500, detail=str(e))
    

# HTTP endpoint для управления сессией
@router.post("/control_stream/{session_id}")
async def control_stream(session_id: str, request: ControlStreamRequest):
    if session_id not in session_state.active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Получаем клиент из сессии
        client = session_state.active_sessions[session_id]["client"]
        session_info = await client.control_stream(
            request.action,
            request.bitrate,
            request.chunk_num
        )
        
            
        if session_info['status'] == 'STOPPED':
            await grpc_client._cleanup_session(session_id)
            grpc_client.stream = None
        else:
        # Обновляем информацию
            session_state.active_sessions[session_id]["info"] = session_info
        
        return {
            "session_id": session_info["session_id"],
            "current_bitrate": session_info["current_bitrate"],
            "available_bitrates": session_info["available_bitrates"],
            "current_chunk": session_info["current_chunk"],
            "chunk_size": session_info["chunk_size"],
            "total_chunks": session_info["total_chunks"],
            "status": session_info["status"]
        }
    except Exception as e:
        raise
        # raise HTTPException(status_code=500, detail=str(e))
    

# HTTP endpoint для получения информации о сессии
@router.get("/session_info/{session_id}")
async def get_session_info(session_id: str):
    if session_id not in session_state.active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_info = session_state.active_sessions[session_id]["info"]
    return {
        "current_bitrate": session_info["current_bitrate"],
        "available_bitrates": session_info["available_bitrates"],  
        "status": session_info["status"],  
        "current_chunk": session_info["current_chunk"],
        "chunk_size": session_info["chunk_size"],
        "total_chunks": session_info["total_chunks"]
    }
