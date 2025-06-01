from abc import ABC, abstractmethod
from google.protobuf.message import Message
from typing import Dict


class BaseEventConverter(ABC):
    """Абстрактный базовый класс для всех конвертеров событий"""
    
    @staticmethod
    @abstractmethod
    def get_headers(event) -> Dict[str, str]:
        """Должен возвращать заголовки для Kafka сообщения"""
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def to_proto(cls, event) -> Message:
        """Должен конвертировать доменное событие в protobuf-сообщение"""
        raise NotImplementedError
