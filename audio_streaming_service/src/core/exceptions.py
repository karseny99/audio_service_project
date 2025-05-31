class DomainError(Exception):
    pass

class ValueObjectException(ValueError):
    pass

class BitrateNotFound(DomainError):
    pass

class StreamingSessionError(DomainError):
    pass

class AccessFail(ValueError):
    pass

class UnknownMessageReceived(ValueError):
    pass

class InvalidUseOfControlUseCase(ValueError):
    pass

class SessionRepositoryError(Exception):
    pass

class SessionSerializationError(SessionRepositoryError):
    pass

class SessionDeserializationError(SessionRepositoryError):
    pass
