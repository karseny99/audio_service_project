from dataclasses import dataclass

@dataclass(frozen=True)
class Username:
    value: str

    def __post_init__(self):
        if len(self.value) not in range(3, 16) :
            raise ValueError("Bad username's length")
        if not self.value.isalnum():
            raise ValueError("Must contain only digits or letters")
