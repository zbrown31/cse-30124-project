from .location import Location
from .norm import Norm
from .gmaps_client import GMapsClient

class Trip:
    def __init__(self, start: Location, destination: Location, norm: Norm | None = None):
        self.start: Location = start
        self.destination: Location  = destination

        if norm is None:
            self.norm: Norm =  GMapsClient().get_distance(start.coordinates, destination.coordinates)
        else:
            self.norm: Norm  = norm
    