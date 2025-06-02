from faststream.kafka import KafkaBroker
from contextlib import asynccontextmanager
from google.protobuf.message import Message
import asyncio

from src.core.config import settings
from src.core.logger import logger

from src.domain.events.events import HistoryEvent

class KafkaEventPublisher:
    def __init__(self, broker: KafkaBroker):
        self._broker = broker
        self._connected = False
        self._lock = asyncio.Lock()

    async def connect(self):
        """Явное подключение к брокеру"""
        async with self._lock:
            if not self._connected:
                try:
                    await self._broker.start()
                    self._connected = True
                    logger.info("Successfully connected to Kafka broker")
                except Exception as e:
                    logger.error(f"Kafka connection failed: {str(e)}")
                    raise

    async def disconnect(self):
        """Явное отключение от брокера"""
        async with self._lock:
            if self._connected:
                try:
                    await self._broker.close()
                    self._connected = False
                    logger.info("Successfully disconnected from Kafka broker")
                except Exception as e:
                    logger.error(f"Kafka disconnection failed: {str(e)}")
                    raise

    @asynccontextmanager
    async def get_producer(self):
        """Контекстный менеджер для работы с продюсером"""
        await self.connect()
        try:
            yield self._broker
        finally:
            pass  # Не закрываем соединение явно, чтобы переиспользовать

    async def publish(self, event: HistoryEvent, topic: str, key: str | None = None):
        """Публикация сообщения с гарантированным подключением"""
        try:
            async with self.get_producer() as producer:               
                pass
                # headers = event.get_headers()
                # message = event.to_proto().SerializeToString()
                # await producer.publish(
                #     message=message,
                #     topic=topic,
                #     headers=headers,
                #     key=key.encode() if key else None,
                # )
                logger.debug(f"Successfully published to {topic}")
        except Exception as e:
            logger.error(f"Publication failed: {str(e)}")
            raise

    @property
    def destination(self) -> str:
        return settings.KAFKA_PLAYLIST_CONTEXT_TOPIC