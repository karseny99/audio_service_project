# src/core/kafka_producer.py
from kafka import KafkaProducer
import json
from .config import settings

producer = KafkaProducer(
    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send(topic: str, message: dict):
    producer.send(topic, message)
    producer.flush()
