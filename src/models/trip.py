from .location import Location
from .norm import Norm


class Trip:
    def __init__(self, start: Location, destination: Location, norm: Norm):
        self.start: Location = start
        self.destination: Location = destination
        self.norm = norm
