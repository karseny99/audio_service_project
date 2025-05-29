class DomainError(Exception):
    pass

class ValueObjectException(ValueError):
    pass

class InvalidPasswordError(DomainError):
    pass

class TrackNotFoundError(DomainError):
    pass

class InvalidBitrateError(DomainError):
    pass

class StreamingSessionError(DomainError):
    pass

class AccessFail(ValueError):
    pass