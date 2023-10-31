from rider import Rider
from driver import Driver
from trip import Trip
from datetime import datetime
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
        self.cancel_time: datetime | None = None
    
    def cancel(self) -> None:
        self.status = RideStatus.CANCELLED
        self.cancel_time = datetime.now()
    
    def match(self, driver: Driver) -> None:
        self.status = RideStatus.MATCHED
        self.driver = driver
        self.match_time = datetime.now()

    def set_status(self, status:RideStatus) -> None:
        self.status = status

    
