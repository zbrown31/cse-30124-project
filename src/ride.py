from rider import Rider
from driver import Driver
from trip import Trip
from datetime import date, datetime, timedelta
from enum import Enum

class RideStatus(Enum):
    REQUESTED = 0
    MATCHED = 1
    IN_RIDE = 2
    COMPLETED = 3
    CANCELLED = 4

class Ride:
    def __init__(self, rider:Rider, trip:Trip, price: float,  driver:Driver | None = None) -> None:
        self.rider = rider
        self.driver = driver
        self.trip = trip
        self.status: RideStatus = RideStatus.REQUESTED
        self.price = price
        self.request_time: datetime = datetime.now()
        self.match_time: datetime | None = None
        self.pickup_time: datetime | None = None
        self.arrived_time: datetime | None = None
        self.cancel_time: datetime | None = None
        self.time_to_pickup: timedelta = timedelta(seconds=0)
    
    def cancel(self, time:datetime) -> None:
        self.status = RideStatus.CANCELLED
        self.cancel_time = time
    
    def match(self, driver: Driver, time:datetime) -> None:
        self.status = RideStatus.MATCHED
        self.driver = driver
        self.match_time = time

    def picked_up(self, time:datetime) -> None:
        self.status = RideStatus.IN_RIDE
        self.pickup_time = datetime.now()
    
    def arrived(self, time:datetime) -> None:
        self.status = RideStatus.COMPLETED
        self.arrived_time = time

    def set_status(self, status:RideStatus) -> None:
        self.status = status
    
    def get_time_to_match(self) -> int:
        if self.match_time is not None:
            return (self.match_time - self.request_time).total_seconds()
        else:
            return None
    
    def get_time_to_cancel(self) -> int:
        if self.cancel_time is not None:
            return (self.cancel_time - self.request_time).total_seconds()
        else:
            return None
    
    def get_time_to_resolved(self) -> int:
        if self.cancel_time is not None:
            return (self.cancel_time - self.request_time).total_seconds()
        elif self.match_time is not None:
            return (self.match_time - self.request_time).total_seconds()
        else:
            return None
    
    def get_resolved_time(self) -> datetime | None:
        if self.cancel_time is not None:
            return self.cancel_time
        elif self.match_time is not None:
            return self.match_time
        else:
            return None
    
    def get_wait_time(self, current_time: datetime) -> int:
        if self.cancel_time is None and self.pickup_time is None:
            return (current_time  - self.request_time).total_seconds()
        elif self.pickup_time is not None:
            return (self.pickup_time - self.request_time).total_seconds()
        elif self.cancel_time is not None:
            return (self.cancel_time - self.request_time).total_seconds()
    
    

    
