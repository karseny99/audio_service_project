class DomainError(Exception):
    """Базовое исключение для бизнес-ошибок"""

class EmailAlreadyExistsError(DomainError):
    pass

class UsernameAlreadyExistsError(DomainError):
    pass

class ValueObjectException(ValueError):
    pass