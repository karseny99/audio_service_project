from dataclasses import dataclass

@dataclass(frozen=True)
class TrackDuration:
    milliseconds: int

    @property
    def seconds(self) -> float:
        return self.milliseconds / 1000

    def to_hhmmss(self) -> str:
        secs = int(self.seconds)
        mins, secs = divmod(secs, 60)
        hours, mins = divmod(mins, 60)
        return f"{hours:02d}:{mins:02d}:{secs:02d}"

    @classmethod
    def from_hhmmss(cls, time_str: str) -> "TrackDuration":
        """
            Converts HH:MM:SS format to TrackDuration object
        """

        parts = list(map(int, time_str.split(":")))
        if len(parts) == 3:  # HH:MM:SS
            hours, mins, secs = parts
        elif len(parts) == 2:  # MM:SS
            hours, mins, secs = 0, *parts
        else:
            raise ValueError("Format must be HH:MM:SS or MM:SS")
        total_ms = (hours * 3600 + mins * 60 + secs) * 1000
        return cls(total_ms)