from .coordinates import Coordinates


class Location:
    def __init__(self, name: str, address: str, coordinates: Coordinates) -> None:
        self.name = name
        self.address = address
        self.coordinates = coordinates
