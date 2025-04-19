from dataclasses import dataclass

@dataclass(frozen=True)
class PlaylistTitle:
    value: str

    def __post_init__(self):
        if len(self.value) not in range(1, 100):
            print(len(self.value))
            raise ValueError("Название не может быть пустым")
        if "\n" in self.value or "<script>" in self.value:
            raise ValueError("Недопустимые символы")
