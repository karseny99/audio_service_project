from dataclasses import dataclass

@dataclass
class BaseEvent:
    pass

@dataclass
class SearchPerformed(BaseEvent):
    """
    Пример события: кто-то выполнил поиск (можно отправить в Kafka, если нужно).
    """
    query: dict
    timestamp: str
