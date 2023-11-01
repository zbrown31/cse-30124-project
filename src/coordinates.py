from dataclasses import dataclass

@dataclass
class Coordinates:
    latitude: float
    longitude: float

    def to_tuple(self) -> tuple[str,str]:
        return (self.latitude, self.longitude)