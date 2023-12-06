from collections import deque
from datetime import datetime

from src.models import Driver, Ride
from ..dispatcher import Strategy


class BaseStrategy(Strategy):
    def assign_drivers(
        self, rides: list[Ride], drivers: dict[Driver, int], current_time: datetime
    ) -> list[tuple[Ride, Driver]]:
        ride_queue = deque(list(reversed(rides)))
        available_drivers = deque(
            filter(
                lambda x: x.current_ride is None or len(x.ride_queue) == 0,
                drivers.keys(),
            )
        )
        assignments: list[tuple[Ride, Driver]] = []
        while len(ride_queue) > 0 and len(available_drivers) > 0:
            assignments.append((ride_queue.popleft(), available_drivers.popleft()))
        return assignments
