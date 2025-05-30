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