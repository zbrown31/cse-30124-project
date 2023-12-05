from collections import deque
from datetime import datetime, timedelta

from src.models import Driver, Ride
from ..dispatcher import BatchedStrategy

class BatchedGreedyStrategy(BatchedStrategy):
    def assign_drivers(self, rides: list[Ride], drivers: dict[Driver, int], current_time:datetime) -> list[tuple[Ride,Driver]]:
        self.step += 1
        if (self.step % self.batch_time != 0):
            return []
        ride_queue = deque(rides)
        available_drivers = deque(filter(lambda x: (x.current_ride is None or len(x.ride_queue) == 0), drivers.keys()))
        
        assignments: list[tuple[Ride, Driver]] = []

        while len(ride_queue) > 0 and len(available_drivers) > 0:
            ride = ride_queue[0]
            pickup_times: list[timedelta] = []
            for driver in available_drivers:
                pickup_times.append(driver.get_time_away(ride.trip.start, current_time))
            if len(pickup_times) > 0:
                assignments.append((ride, sorted(list(zip(pickup_times, available_drivers)), key=lambda x: x[0])[0][1]))
                ride_queue.popleft()
                available_drivers.popleft()
            return assignments
        else:
            return []