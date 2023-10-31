from location import Location
from gmaps_client import GMapsClient

class Trip:
    def __init__(self, start: Location, destination: Location):
        self.start = start
        self.destination  = destination
        self.distance = GMapsClient().get_distance(self.start, self.destination)
    