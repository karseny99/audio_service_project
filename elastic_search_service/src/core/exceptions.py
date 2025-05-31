class DomainError(Exception):
    """Базовый класс для доменных ошибок."""

class ValueObjectException(ValueError):
    """Ошибка валидации value object."""

class ExternalServiceError(RuntimeError):
    """Ошибка внешнего сервиса (например, Elasticsearch)."""

class NotFoundError(DomainError):
    """Сущность не найдена."""
