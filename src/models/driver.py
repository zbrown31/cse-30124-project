from collections import deque
from datetime import timedelta, datetime
from .location import Location
from .ride import Ride


class Driver:
    def __init__(self, name: str):
        self.name = name
        self.current_ride = None
        self.ride_queue: deque[Ride] = deque()
        self.ride_history: list[Ride] = []

    def add_ride(self, ride: Ride) -> None:
        if self.current_ride is None:
            self.current_ride = ride
        else:
            self.ride_queue.append(ride)

    def finish_current_ride(self) -> None:
        if self.current_ride is not None:
            self.ride_history.append(self.current_ride)
        if len(self.ride_queue) == 0:
            self.current_ride = None
        else:
            self.current_ride = self.ride_queue.popleft()

    def get_time_away(self, destination: Location, current_time: datetime) -> timedelta:
        time_remaining = None
        if len(self.ride_queue) > 0:
            if self.current_ride is not None:
                current_ride_time_remaining = self.current_ride.get_time_remaining(
                    current_time
                )
            else:
                current_ride_time_remaining = timedelta(seconds=0)
            queued_ride_time_remaining = self.ride_queue[0].get_time_remaining(
                current_time
            )
            if (
                current_ride_time_remaining is not None
                and queued_ride_time_remaining is not None
            ):
                time_remaining = (
                    current_ride_time_remaining + queued_ride_time_remaining
                )
        elif self.current_ride is not None:
            time_remaining = self.current_ride.get_time_remaining(current_time)

        if time_remaining is None:
            return timedelta(seconds=60 * 7)
        else:
            return time_remaining

    def get_ride_history(self) -> list[Ride]:
        return self.ride_history

    def get_ride_queue(self) -> deque[Ride]:
        return self.ride_queue
