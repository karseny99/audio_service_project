from google.protobuf.message import Message
from faststream.kafka import KafkaBroker, KafkaMessage
from typing import Type, Dict
from dataclasses import dataclass

from src.core.logger import logger
from src.core.config import settings

from src.domain.events.handlers import EventHandler


@dataclass
class EventTypeMapping:
    proto_type: Type[Message]
    handler: EventHandler

class KafkaConsumer:
    def __init__(
        self,
        broker: KafkaBroker,
        topic: str,
        event_mappings: Dict[str, EventTypeMapping]
    ):
        self._broker = broker
        self._topic = topic
        self._event_mappings = event_mappings
        self._handler = None  # Будем хранить обработчик

    async def start(self):
        # 1. Сначала объявляем подписку
        @self._broker.subscriber(self._topic)
        async def on_message(msg: KafkaMessage):
            try:
                event_type = msg.headers.get(settings.EVENT_HEADER)
                if not event_type:
                    logger.warning(f"Message without event-type: {msg}")
                    return
                
                if event_type not in self._event_mappings:
                    logger.warning(f"Unknown event type: {event_type}")
                    return
                

                mapping = self._event_mappings[event_type]
                proto_message = mapping.proto_type()
                proto_message.ParseFromString(msg.body)
                
                logger.debug(f"Event received: {proto_message}")
                await mapping.handler.handle(proto_message)
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                raise
        
        self._handler = on_message  # Сохраняем ссылку
        
        # 2. Только потом запускаем брокер
        await self._broker.start()
        logger.info(f"Consumer started for topic: {self._topic}")    
