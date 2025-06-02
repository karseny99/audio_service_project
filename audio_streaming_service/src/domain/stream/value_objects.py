from src.core.exceptions import ValueObjectException

class Bitrate:
    SUPPORTED = [128, 192, 320]

    def __init__(self, value: int):
        if value not in self.SUPPORTED:
            raise ValueObjectException("Unsupported bitrate")
        self.value = value

class StreamOffset:
    def __init__(self, value: int, max_offset: int):
        if value < 0 or value > max_offset:
            raise ValueObjectException("Offset out of range")
        self.value = value
