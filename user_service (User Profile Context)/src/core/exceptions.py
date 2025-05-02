class DomainError(Exception):
    """Базовое исключение для бизнес-ошибок"""

class EmailAlreadyExistsError(DomainError):
    pass

class ValueObjectException(ValueError):
    pass