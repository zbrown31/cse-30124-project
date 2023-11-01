from dataclasses import dataclass
from multipledispatch import dispatch
from coordinates import Coordinates
from gmaps_client import GMapsClient
from norm import Norm


class Location:
    def __init__(self, name: str, address:str, coordinates:Coordinates) -> None:
        self.name = name
        self.address = address
        self.coordinates = coordinates
    
    def norm(self, other:"Location") -> Norm:
        return GMapsClient().get_distance(self.coordinates, other.coordinates)

    @staticmethod
    def get_location(name: str, address:str) -> "Location":
        return Location(name=name, address=address, coordinates=GMapsClient().address_to_coordinates(address=address))

    @staticmethod
    def get_location(name:str, coordinates: Coordinates) -> "Location":
        return Location(name=name, address=GMapsClient().coordinates_to_address(coordinates=coordinates), coordinates=coordinates)