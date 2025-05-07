from dependency_injector import containers, providers
from .kafka_producer import KafkaProducer

class Container(containers.DeclarativeContainer):
    kafka_producer = providers.Singleton(KafkaProducer)
