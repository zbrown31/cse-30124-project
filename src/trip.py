from location import Location
from norm import Norm

class Trip:
    def __init__(self, start: Location, destination: Location):
        self.start: Location = start
        self.destination: Location  = destination
        self.norm: Norm =  self.start.norm(self.destination)
    