from .location import Location
from .norm import Norm

class Trip:
    def __init__(self, start: Location, destination: Location, norm: Norm | None = None):
        self.start: Location = start
        self.destination: Location  = destination

        if norm is None:
            self.norm: Norm =  self.start.norm(self.destination)
        else:
            self.norm: Norm  = norm
    