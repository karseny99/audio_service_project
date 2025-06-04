from abc import ABC, abstractmethod
import grpc
from typing import Type, TypeVar, Generic
from google.protobuf.message import Message
from src.core.config import settings
from src.core.logger import logger
from src.core.exceptions import ExternalServiceError

T = TypeVar('T')  # Generic для stub-класса

class BaseGrpcClient(ABC, Generic[T]):
    def __init__(self):
        self._channel = None
        self._stub = None
        self._timeout = settings.GRPC_TIMEOUT

    @property
    @abstractmethod
    def stub_class(self) -> Type[T]:
        """Должен возвращать класс gRPC stub (сгенерированный protobuf)"""
        pass

    @property
    @abstractmethod
    def service_address(self) -> str:
        """Должен возвращать адрес сервиса (например: 'track-service:50051' ||| щас отличие тока в портах для запуска в localhost) """ 
        pass

    async def connect(self) -> None:
        try:
            self._channel = grpc.aio.insecure_channel(self.service_address)
            self._stub = self.stub_class(self._channel)
            logger.info(f"Connected to {self.service_address}")
        except Exception as e:
            logger.error(f"Connection failed to {self.service_address}: {str(e)}")
            raise ExternalServiceError("gRPC connection failed")

    async def disconnect(self) -> None:
        if self._channel:
            await self._channel.close()
            logger.info(f"Disconnected from {self.service_address}")

    async def _call(
        self,
        method_name: str,
        request: Message,
        timeout: int = None
    ) -> Message:
        if not self._stub:
            await self.connect()

        try:
            method = getattr(self._stub, method_name)
            return await method(request, timeout=timeout or self._timeout)
        except grpc.RpcError as e:
            logger.error(f"gRPC call failed: {method_name} | {e.code()}: {e.details()}")
            raise ExternalServiceError(f"Service error: {e.details()}")
        except Exception as e:
            logger.error(f"Unexpected error in {method_name}: {str(e)}")
            raise ExternalServiceError("Internal client error")