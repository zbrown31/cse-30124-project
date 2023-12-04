from collections import deque
from datetime import timedelta, datetime
from .norm import Norm
from .gmaps_client import GMapsClient
from .location import Location

class Driver:
    def __init__(self, name):
        self.name = name
        self.current_ride = None
        self.ride_queue: deque = deque()
        self.ride_history: list = []
    
    def add_ride(self, ride) -> None:
        if self.current_ride is None:
            self.current_ride = ride
        else:
            self.ride_queue.append(ride)
    
    def finish_current_ride(self) -> None:
        self.ride_history.append(self.current_ride)
        if len(self.ride_queue) == 0:
            self.current_ride = None
        else:
            self.current_ride = self.ride_queue.popleft()
    
    def get_time_away(self, mapper: GMapsClient, destination: Location, current_time: datetime) -> timedelta:
        time_remaining = None
        if self.current_ride is not None:
            time_remaining =  self.current_ride.get_time_remaining(current_time)
        elif len(self.ride_queue) > 0:
            current_ride_time_remaining = self.current_ride.get_time_remaining(current_time)
            queued_ride_time_remaining = self.queued_ride.get_time_remaining(current_time)
            if current_ride_time_remaining is not None and queued_ride_time_remaining is not None:
                time_remaining = current_ride_time_remaining + queued_ride_time_remaining
        elif len(self.ride_history) > 0:
            time_remaining = mapper.get_distance(self.ride_history[-1].trip.destination.coordinates, destination.coordinates).duration
        
        if time_remaining is None:
            return timedelta(seconds=60 * 7)
        else:
            return time_remaining

    def get_ride_history(self) -> list:
        return self.ride_history
    
    def get_ride_queue(self) -> deque:
        return self.ride_queue