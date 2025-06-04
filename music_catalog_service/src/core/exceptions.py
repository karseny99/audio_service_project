class DomainError(Exception):
    """Базовое исключение для бизнес-ошибок"""

class TrackAlreadyInPlaylist(DomainError):
    pass

class ValueObjectException(ValueError):
    pass

class ExternalServiceError(RuntimeError):
    pass

class TrackNotFound(DomainError):
    pass

class InsufficientPermission(PermissionError):
    pass