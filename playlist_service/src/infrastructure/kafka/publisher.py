from faststream.kafka import KafkaBroker
from google.protobuf.message import Message
from src.core.config import settings
from src.core.logger import logger
import asyncio
from contextlib import asynccontextmanager

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

    async def publish(self, event: Message, topic: str, key: str | None = None):
        """Публикация сообщения с гарантированным подключением"""
        try:
            async with self.get_producer() as producer:
                message = event.SerializeToString()
                await producer.publish(
                    message=message,
                    topic=topic,
                    key=key.encode() if key else None,
                )
                logger.debug(f"Successfully published to {topic}")
        except Exception as e:
            logger.error(f"Publication failed: {str(e)}")
            raise

    @property
    def destination(self) -> str:
        return settings.KAFKA_USER_CONTEXT_TOPIC