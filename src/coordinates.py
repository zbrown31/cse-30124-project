from dataclasses import dataclass

@dataclass
class Coordinates:
    latitude: float
    longitude: float

    def to_tuple(self) -> tuple[float,float]:
        return (self.latitude, self.longitude)
    
    def __hash__(self) -> int:
        return hash((self.latitude, self.longitude))

    def __eq__(self, other: "Coordinates") -> bool:
        return self.latitude == other.latitude and self.longitude == other.longitude