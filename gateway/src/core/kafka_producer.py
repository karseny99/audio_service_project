# до этого вы, наверное, делали:
# producer = KafkaProducer(...)

from kafka import KafkaProducer
import json
from .config import settings

_producer: KafkaProducer | None = None

def _create_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )

def get_producer() -> KafkaProducer:
    global _producer
    if _producer is None:
        _producer = _create_producer()
    return _producer

def send(topic: str, message: dict) -> None:
    try:
        p = get_producer()
        p.send(topic, message)
        p.flush()
    except Exception as e:
        # можно логировать, но не выбрасывать дальше
        # например: logger.warning(f"Failed to send to Kafka: {e}")
        pass
