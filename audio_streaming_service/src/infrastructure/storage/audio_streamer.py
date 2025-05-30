import math
from minio import Minio
from typing import Generator, Optional, Union, List
from dependency_injector.wiring import inject, Provide

from src.core.config import settings
from src.core.logger import logger
from src.core.exceptions import BitrateNotFound
from src.core.exceptions import AccessFail
from src.domain.stream.repository import AudioStreamer, AudioChunk


class S3AudioStreamer(AudioStreamer):
    @inject
    def __init__(
        self,
        bucket_name: str,
        minio_client: Minio,
        chunk_size: int = 32768,
        path: str = "",
    ):
        """
        :param bucket_name: имя бакета
        :param minio_client: клиент MinIO
        :param chunk_size: размер чанка в байтах
        :param path: базовый путь к трекам
        """
        self.minio_client = minio_client
        self.bucket_name = bucket_name
        self.chunk_size = chunk_size
        self.path = path
        
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

    def initialize(self, track_id: str, initial_bitrate: str) -> None:
        """
        Инициализирует стример для конкретного трека
        :param track_id: ID трека
        :param initial_bitrate: начальный битрейт
        """
        self.track_id = track_id
        self.current_bitrate = initial_bitrate
        self._refresh_object_info()
        self._initialized = True

    def _validate_initialized(self):
        """Проверяет, что стример инициализирован"""
        if not self._initialized:
            raise RuntimeError("S3AudioStreamer not initialized. Call initialize() first")

    def _get_object_name(self) -> str:
        """Генерирует имя объекта в MinIO"""
        return f"{self.path}/{self.track_id}/{self.current_bitrate}.mp3"

    def _refresh_object_info(self):
        """Обновляет метаданные текущего аудиофайла"""
        self.object_name = self._get_object_name()
        try:
            self.available_bitrates = self.get_bitrates()
            
            self.object_stat = self.minio_client.stat_object(
                self.bucket_name, 
                self.object_name
            )
            self.object_size = self.object_stat.size
            self.duration_seconds = float(getattr(
                self.object_stat.metadata,
                'x-amz-meta-duration',
                self._estimate_duration()
            ))
        except Exception as e:
            raise AccessFail(f"Error accessing {self.object_name}: {str(e)}")

    def _estimate_duration(self) -> float:
        """Оценивает длительность на основе битрейта и размера файла"""
        bitrate_kbps = int(self.current_bitrate)
        return (self.object_size * 8) / (bitrate_kbps * 1000)
    
    def get_bitrates(self) -> List[str]:
        """
        Возвращает список доступных битрейтов для текущего трека
        """
        try:
            prefix = f"{self.path}{self.track_id}/"
            
            objects = self.minio_client.list_objects(
                self.bucket_name,
                prefix=prefix,
                recursive=False
            )
            
            bitrates = []
            for obj in objects:
                if obj.object_name.endswith('.mp3'):
                    filename = obj.object_name.split('/')[-1]
                    bitrate = filename.replace('.mp3', '')
                    if bitrate.isdigit():
                        bitrates.append(bitrate)
            
            return sorted(bitrates, key=lambda x: int(x), reverse=True)
            
        except Exception as e:
            logger.info(f"Error getting available bitrates: {str(e)}")
            return []

    def switch_bitrate(self, new_bitrate: str):
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
        self._refresh_object_info()
        
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

    def read_chunk(self, offset: Optional[Union[int, float]] = None) -> bytes:
        """
        Читает чанк данных
        
        :param offset: смещение в байтах (int) или секундах (float)
        :return: аудиоданные
        """
        self._validate_initialized()

        # Обработка параметра offset
        if offset is not None:
            if isinstance(offset, float):
                self.set_current_time(offset)
            else:
                self.seek(offset)

        if self.current_offset >= self.object_size:
            return b''

        try:
            response = self.minio_client.get_object(
                self.bucket_name,
                self.object_name,
                offset=self.current_offset,
                length=min(self.chunk_size, self.object_size - self.current_offset)
            )
            
            chunk_data = response.read()
            self.current_offset += len(chunk_data)
            return chunk_data
        except Exception as e:
            raise RuntimeError(f"Error reading chunk: {str(e)}")
        finally:
            response.close()
            response.release_conn()

    def seek(self, offset_bytes: int):
        """
        Устанавливает позицию в байтах
        
        :param offset_bytes: смещение в байтах
        """
        self._validate_initialized()

        if not 0 <= offset_bytes < self.object_size:
            raise ValueError(f"Offset must be between 0 and {self.object_size - 1}")
        self.current_offset = offset_bytes

    def chunks(self, start_pos: Union[int, float] = 0) -> Generator[AudioChunk, None, None]:
        """
        Генератор для последовательного чтения чанков
        
        :param start_pos: начальная позиция в байтах (int) или секундах (float)
        :yield: чанки аудиоданных

        @dataclass
        class AudioChunk:
            data: bytes
            number: int  # Порядковый номер (соответствует current_chunk сессии)
            is_last: bool
            bitrate: str 
        """
        self._validate_initialized()

        if isinstance(start_pos, float):
            self.set_current_time(start_pos)
        else:
            self.seek(start_pos)

        self.chunk_counter = 0
        remaining_bytes = self.object_size - self.current_offset

        while remaining_bytes > 0:
            chunk_data = self.read_chunk()
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
        return (self.object_size + self.chunk_size - 1) // self.chunk_size
