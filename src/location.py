from dataclasses import dataclass

@dataclass
class Coordinates:
    latitude: float
    longitude: float

    def to_tuple(self) -> tuple[str,str]:
        return (self.latitude, self.longitude)

class Location:
    def __init__(self, name: str, address:str, coordinates:Coordinates) -> None:
        self.name = name
        self.address = address
        self.coordinates = coordinates
    
    @staticmethod
    def get_location(name: str, address:str) -> "Location":
        pass

    @staticmethod
    def get_location(name:str, coordinates: Coordinates) -> "Location":
        pass