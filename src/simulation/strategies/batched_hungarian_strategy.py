from collections import deque
from datetime import datetime

import numpy as np
from scipy import optimize

from src.models import Driver, Ride
from ..dispatcher import BatchedStrategy


class BatchedHungarianStrategy(BatchedStrategy):
    def assign_drivers(
        self, rides: list[Ride], drivers: dict[Driver, int], current_time: datetime
    ) -> list[tuple[Ride, Driver]]:
        self.step += 1
        if self.step % self.batch_time != 0:
            return []
        else:
            available_drivers = deque(
                filter(
                    lambda x: (x.current_ride is None or len(x.ride_queue) <= 1),
                    drivers.keys(),
                )
            )
            if len(rides) == 0 or len(available_drivers) == 0:
                return []
            cost_matrix = np.zeros(shape=(len(rides), len(drivers)))
            drivers_list = list(drivers.keys())
            for ride_index, ride in enumerate(rides):
                for driver_index, driver in enumerate(drivers_list):
                    cost_matrix[ride_index, driver_index] = driver.get_time_away(
                        ride.trip.start, current_time
                    ).total_seconds()
            row_indexes, col_indexes = optimize.linear_sum_assignment(
                cost_matrix
            )  # ignore: type
            return list(
                map(
                    lambda x: (rides[x[0]], drivers_list[x[1]]),
                    list(zip(list(row_indexes), list(col_indexes))),
                )
            )
