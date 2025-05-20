class DomainError(Exception):
    """Базовое исключение для бизнес-ошибок"""

class TrackAlreadyLiked(DomainError):
    pass

class ValueObjectException(ValueError):
    pass

class ExternalServiceError(RuntimeError):
    pass

class TrackNotFoundError(DomainError):
    pass

class InsufficientPermission(PermissionError):
    pass