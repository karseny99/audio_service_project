import math
from typing import Generator, Optional, Union, List, AsyncGenerator
from dependency_injector.wiring import inject, Provide
from aiobotocore.session import get_session

from src.core.logger import logger
from src.core.exceptions import BitrateNotFound
from src.core.exceptions import AccessFail
from src.domain.stream.repository import AudioStreamer, AudioChunk


class S3AudioStreamer(AudioStreamer):
    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        endpoint_url: str,
        chunk_size: int = 32768,
        path: str = "",
    ):
        """
        :param bucket_name: имя бакета
        :param aws_access_key_id: AWS access key (или MinIO access key)
        :param aws_secret_access_key: AWS secret key (или MinIO secret key)
        :param endpoint_url: URL endpoint S3/MinIO
        :param chunk_size: размер чанка в байтах
        :param path: базовый путь к трекам
        """
        self.bucket_name = bucket_name
        self._chunk_size = chunk_size
        self.path = path
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key 
        self.endpoint_url = endpoint_url
        
        # Поля, которые будут инициализированы после вызова initialize()
        self.track_id: Optional[str] = None
        self.current_bitrate: Optional[str] = None
        self.available_bitrates: List[str] = []
        self.object_stat = None
        self.object_size = 0
        self.duration_seconds = 0.0
        self.current_offset = 0
        self.chunk_counter = 0
        self._initialized = False
        self._s3_client = None

    async def _get_client(self):
        """Ленивая инициализация клиента"""
        if self._s3_client is None:
            session = get_session()
            self._s3_client = await session.create_client(
                's3',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                endpoint_url=self.endpoint_url,
                region_name='us-east-1',
            ).__aenter__()
        return self._s3_client

    async def close(self):
        """Закрытие клиента"""
        if self._s3_client is not None:
            await self._s3_client.close()
            self._s3_client = None


    async def initialize(self, track_id: str, initial_bitrate: str) -> None:
        """
        Инициализирует стример для конкретного трека
        :param track_id: ID трека
        :param initial_bitrate: начальный битрейт
        """           
        self.track_id = track_id
        self.current_bitrate = initial_bitrate
        await self._refresh_object_info()
        self._initialized = True

    def _validate_initialized(self):
        """Проверяет, что стример инициализирован"""
        if not self._initialized:
            raise RuntimeError("AsyncS3AudioStreamer not initialized. Call initialize() first")

    def _get_object_name(self) -> str:
        """Генерирует имя объекта в S3/MinIO"""
        return f"{self.path}/{self.track_id}/{self.current_bitrate}.mp3"

    async def _refresh_object_info(self):
        self.object_name = self._get_object_name()
        try:
            client = await self._get_client()
            self.available_bitrates = await self.get_bitrates()
            
            head_response = await client.head_object(
                Bucket=self.bucket_name,
                Key=self.object_name
            )
            
            self.object_size = head_response['ContentLength']
            self.duration_seconds = float(head_response.get(
                'Metadata', {}
            ).get('duration', self._estimate_duration()))
            
        except Exception as e:
            raise AccessFail(f"Error accessing {self.object_name}: {str(e)}")

    def _estimate_duration(self) -> float:
        """Оценивает длительность на основе битрейта и размера файла"""
        bitrate_kbps = int(self.current_bitrate)
        return (self.object_size * 8) / (bitrate_kbps * 1000)
    
    async def get_bitrates(self) -> List[str]:
        try:
            client = await self._get_client()
            prefix = f"{self.path}{self.track_id}/"
            
            paginator = client.get_paginator('list_objects_v2')
            async for result in paginator.paginate(
                Bucket=self.bucket_name,
                Prefix=prefix,
                Delimiter='/'
            ):
                bitrates = []
                for obj in result.get('Contents', []):
                    key = obj['Key']
                    if key.endswith('.mp3'):
                        filename = key.split('/')[-1]
                        bitrate = filename.replace('.mp3', '')
                        if bitrate.isdigit():
                            bitrates.append(bitrate)
                
                return sorted(bitrates, key=lambda x: int(x), reverse=True)
            
            return []
        except Exception as e:
            logger.info(f"Error getting available bitrates: {str(e)}")
            return []

    async def switch_bitrate(self, new_bitrate: str):
        """
        Переключает битрейт с сохранением временной позиции
        
        :param new_bitrate: новый битрейт ('128k', '320k' и т.д.)
        """
        self._validate_initialized()
        if new_bitrate == self.current_bitrate:
            return

        if new_bitrate not in self.available_bitrates:
            raise BitrateNotFound("No such bitrate found")

        # Сохраняем текущую позицию в секундах
        current_time = self.get_current_time()
        
        # Переключаемся на новый битрейт
        self.current_bitrate = new_bitrate
        await self._refresh_object_info()
        
        # Восстанавливаем позицию в новом файле
        self.set_current_time(current_time)

    def get_current_time(self) -> float:
        """
        Возвращает текущую позицию в секундах
        
        :return: позиция в секундах с плавающей точкой
        """
        self._validate_initialized()
        bitrate_kbps = int(self.current_bitrate)
        bytes_per_second = (bitrate_kbps * 1000) / 8
        return self.current_offset / bytes_per_second

    def set_current_time(self, seconds: float):
        """
        Устанавливает текущую позицию в секундах
        
        :param seconds: позиция в секундах
        """
        self._validate_initialized()

        bitrate_kbps = int(self.current_bitrate)
        bytes_per_second = (bitrate_kbps * 1000) / 8
        new_offset = int(seconds * bytes_per_second)
        
        # Обеспечиваем, чтобы позиция была в пределах файла
        self.current_offset = max(0, min(new_offset, self.object_size - 1))

    async def read_chunk(self, offset: Optional[Union[int, float]] = None) -> bytes:
        self._validate_initialized()

        if offset is not None:
            if isinstance(offset, float):
                self.set_current_time(offset)
            else:
                self.seek(offset)

        if self.current_offset >= self.object_size:
            return b''

        try:
            client = await self._get_client()
            response = await client.get_object(
                Bucket=self.bucket_name,
                Key=self.object_name,
                Range=f"bytes={self.current_offset}-{min(self.current_offset + self._chunk_size - 1, self.object_size - 1)}"
            )
            
            async with response['Body'] as stream:
                chunk_data = await stream.read()
                self.current_offset += len(chunk_data)
                return chunk_data
        except Exception as e:
            raise RuntimeError(f"Error reading chunk: {str(e)}")

    def seek(self, offset_bytes: int):
        """
        Устанавливает позицию в байтах
        
        :param offset_bytes: смещение в байтах
        """
        self._validate_initialized()

        if not 0 <= offset_bytes < self.object_size:
            raise ValueError(f"Offset must be between 0 and {self.object_size - 1}")
        self.current_offset = offset_bytes

    async def chunks(self, start_pos: Union[int, float] = 0) -> AsyncGenerator[AudioChunk, None]:
        """
        Асинхронный генератор для последовательного чтения чанков
        
        :param start_pos: начальная позиция в байтах (int) или секундах (float)
        :yield: чанки аудиоданных
        """
        self._validate_initialized()

        if isinstance(start_pos, float):
            self.set_current_time(start_pos)
        else:
            self.seek(start_pos)

        self.chunk_counter = 0
        remaining_bytes = self.object_size - self.current_offset

        while remaining_bytes > 0:
            chunk_data = await self.read_chunk()
            if not chunk_data:
                break
                
            is_last = (self.current_offset >= self.object_size) or \
                     (remaining_bytes - len(chunk_data) <= 0)
            
            yield AudioChunk(
                data=chunk_data,
                number=self.chunk_counter,
                is_last=is_last,
                bitrate=self.current_bitrate,
            )
            
            self.chunk_counter += 1
            remaining_bytes = self.object_size - self.current_offset

    @property
    def bitrate(self) -> str:
        """Возвращает текущий битрейт"""
        self._validate_initialized()
        return self.current_bitrate

    @property
    def duration(self) -> float:
        """Возвращает длительность трека в секундах"""
        self._validate_initialized()
        return self.duration_seconds
    
    @property
    def total_chunks(self) -> int:
        self._validate_initialized()
        return (self.object_size + self._chunk_size - 1) // self._chunk_size
    

    @property
    def chunk_size(self) -> int:
        '''
            size of single chunk in bytes
        '''
        self._validate_initialized()
        return self._chunk_size
