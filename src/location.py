from dataclasses import dataclass
from multipledispatch import dispatch
from .coordinates import Coordinates
from .gmaps_client import GMapsClient
from .norm import Norm


class Location:
    def __init__(self, name: str, address:str, coordinates:Coordinates) -> None:
        self.name = name
        self.address = address
        self.coordinates = coordinates
    
    def norm(self, other:"Location") -> Norm:
        return GMapsClient().get_distance(self.coordinates, other.coordinates)