from datetime import datetime, timedelta
from enum import Enum

from .trip import Trip


class RideStatus(Enum):
    REQUESTED = 0
    MATCHED = 1
    IN_RIDE = 2
    COMPLETED = 3
    CANCELLED = 4


class Ride:
    def __init__(
        self,
        trip: Trip,
        price: float,
        request_time: datetime,
        driver_id: int | None = None,
    ) -> None:
        self.driver_id = driver_id
        self.trip = trip
        self.status: RideStatus = RideStatus.REQUESTED
        self.price = price
        self.request_time: datetime = request_time
        self.match_time: datetime | None = None
        self.pickup_time: datetime | None = None
        self.arrived_time: datetime | None = None
        self.cancel_time: datetime | None = None
        self.time_to_pickup: timedelta | None = None
        self.expected_cancel_time: datetime | None = None

    def cancel(self, time: datetime) -> None:
        self.status = RideStatus.CANCELLED
        self.cancel_time = time

    def match(self, driver_id: int, time: datetime, time_to_pickup: timedelta) -> None:
        self.status = RideStatus.MATCHED
        self.driver_id = driver_id
        self.match_time = time
        self.time_to_pickup = time_to_pickup

    def picked_up(self, time: datetime) -> None:
        self.status = RideStatus.IN_RIDE
        self.pickup_time = time

    def arrived(self, time: datetime) -> None:
        self.status = RideStatus.COMPLETED
        self.arrived_time = time

    def set_status(self, status: RideStatus) -> None:
        self.status = status

    def set_cancel_time(self, cancel_time: datetime):
        self.expected_cancel_time = cancel_time

    def will_cancel(self, current_time: datetime) -> bool:
        if self.expected_cancel_time is not None:
            return current_time > self.expected_cancel_time
        else:
            return False

    def get_time_to_match(self) -> float | None:
        if self.match_time is not None:
            return (self.match_time - self.request_time).total_seconds()
        else:
            return None

    def get_time_to_cancel(self) -> float | None:
        if self.cancel_time is not None:
            return (self.cancel_time - self.request_time).total_seconds()
        else:
            return None

    def get_time_to_resolved(self) -> float | None:
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

    def get_wait_time(self, current_time: datetime) -> float | None:
        if self.cancel_time is None and self.pickup_time is None:
            return (current_time - self.request_time).total_seconds()
        elif self.pickup_time is not None:
            return (self.pickup_time - self.request_time).total_seconds()
        elif self.cancel_time is not None:
            return (self.cancel_time - self.request_time).total_seconds()

    def get_time_remaining(self, current_time: datetime) -> timedelta | None:
        if self.status == RideStatus.CANCELLED or self.status == RideStatus.REQUESTED:
            return None
        elif self.status == RideStatus.COMPLETED:
            return timedelta(seconds=0)
        elif self.status == RideStatus.IN_RIDE:
            if self.pickup_time is None:
                return None
            time_remaining = (self.pickup_time + self.trip.norm.duration) - current_time
            if time_remaining.total_seconds() > 0:
                return time_remaining
            else:
                return timedelta(seconds=0)
        elif self.status == RideStatus.MATCHED:
            if self.match_time is None or self.time_to_pickup is None:
                return None
            time_remaining = (
                self.match_time + self.time_to_pickup + self.trip.norm.duration
            ) - current_time
        else:
            return None
