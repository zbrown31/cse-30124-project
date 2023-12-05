from abc import ABC, abstractmethod
from collections import deque
from datetime import datetime, timedelta

import numpy as np
from scipy import optimize

from src import gmaps_client

from .canceller import Canceller, ChiCanceller
from .clock import Clock
from .driver import Driver
from .metric import Metric
from .ride import Ride, RideStatus


class Dispatcher:
    def __init__(self, ride_requests: list[Ride], drivers: list[Driver], strategy:"Strategy", canceller: Canceller, mapper: gmaps_client.GMapsClient): 
        self.ride_requests = sorted(ride_requests, key=(lambda x: x.request_time))
        self.start_time = self.ride_requests[0].request_time
        resolved_time = self.ride_requests[-1].get_resolved_time()
        if resolved_time is not None:
            self.end_time = resolved_time
        else:
            self.end_time = self.start_time
        self.drivers = drivers
        self.online_drivers = drivers
        self.strategy = strategy
        self.clock = Clock(self.start_time, self.end_time)
        self.canceller = canceller
        self.mapper = mapper
    
    def assign_ride(self, ride: Ride) -> None:
        assigned_driver = self.strategy.choose_driver(ride, self.drivers)
        assigned_driver.add_ride(ride)
    
    def simulate_rides(self) -> list[Ride]:
        ride_start_index: int = 0
        requested_rides: list[Ride] = []
        active_rides: list[Ride] = []
        resolved_rides: list[Ride] = []
        while len(resolved_rides) < len(self.ride_requests):
            current_time = self.clock.get_current_time()
            # print(current_time)
            while ride_start_index < len(self.ride_requests) and self.ride_requests[ride_start_index].request_time < current_time:
                requested_rides.append(self.ride_requests[ride_start_index])
                requested_rides[-1].set_cancel_time(current_time, self.canceller)
                ride_start_index += 1

            driver_assignments = self.strategy.assign_drivers(requested_rides, self.online_drivers, current_time)

            for assignment in driver_assignments:
                ride = assignment[0]
                driver = assignment[1]
                if driver.current_ride is not None:
                    time_to_pickup = self.mapper.get_distance(driver.current_ride.trip.destination.coordinates, ride.trip.start.coordinates).duration
                else:
                    time_to_pickup = timedelta(seconds=(60 * 7) * (np.random.standard_normal() ** 2))
                ride.match(driver, current_time, time_to_pickup)
                active_rides.append(ride)
                requested_rides.remove(ride)

            for i, ride in enumerate(requested_rides):
                if ride.will_cancel(current_time):
                    ride.cancel(current_time)
                    resolved_rides.append(ride)
                    requested_rides.pop(i)

            for i, ride in reversed(list(enumerate(active_rides))):
                ride = active_rides[i]
                if ride.status == RideStatus.MATCHED and current_time - ride.match_time >= ride.time_to_pickup:
                    ride.picked_up(current_time)
                if ride.status == RideStatus.IN_RIDE and current_time - ride.pickup_time >= ride.trip.norm.duration:
                    ride.arrived(current_time)
                    resolved_rides.append(ride)
                    active_rides.pop(i)
            self.clock.tick()
        return resolved_rides


class Strategy(ABC):
    def __init__(self, mapper: gmaps_client.GMapsClient):
        self.mapper = mapper

    @abstractmethod
    def assign_drivers(self, rides: list[Ride], drivers: list[Driver], current_time:datetime) -> list[tuple[Ride,Driver]] | None:
        pass

    def evaluate(self, metrics: list[Metric], rides: list[Ride], drivers: list[Driver]) -> list[Metric]:
        self.mapper.initialize_cache(list(map(lambda x: (x.trip.start, x.trip.destination), rides)))
        dispatcher = Dispatcher(rides, drivers, self, ChiCanceller(10*60, 5*60), self.mapper)
        assignments = dispatcher.simulate_rides()
        for metric in metrics:
            metric.calculate(ride_assignments=assignments)
        return metrics


class BatchedStrategy(Strategy):
    def __init__(self, mapper: gmaps_client.GMapsClient, batch_time: int) -> "GreedyStrategy":
        self.mapper = mapper
        self.batch_time = batch_time
        self.step = -1


class BaseStrategy(Strategy):
    def assign_drivers(self, rides: list[Ride], drivers: list[Driver], current_time:datetime) -> list[tuple[Ride, Driver]] | None:
        ride_queue = deque(list(reversed(rides)))
        available_drivers = deque(filter(lambda x: x.current_ride is None or len(x.ride_queue) == 0, drivers))
        assignments = []
        while len(ride_queue) > 0 and len(available_drivers) > 0:
            assignments.append((ride_queue.popleft(), available_drivers.popleft()))
        return assignments



class GreedyStrategy(Strategy):
    def __init__(self, mapper: gmaps_client.GMapsClient):
        self.mapper = mapper
    def assign_drivers(self, rides: list[Ride], drivers: list[Driver], current_time: datetime) -> list[tuple[Ride, Driver]] | None:
        ride_queue = deque(rides)
        available_drivers = deque(filter(lambda x: (x.current_ride is None or len(x.ride_queue) <= 1), drivers))
        assignments = []
        while len(ride_queue) > 0 and len(available_drivers) > 0:
            ride = ride_queue[0]
            pickup_times = []
            for driver in available_drivers:
                pickup_times.append(driver.get_time_away(self.mapper, ride.trip.start, current_time))
            if len(pickup_times) > 0:
                assignments.append((ride, sorted(list(zip(pickup_times, available_drivers)), key=lambda x: x[0])[0][1]))
                ride_queue.popleft()
                available_drivers.popleft()
        return assignments


class BatchedGreedyStrategy(BatchedStrategy):
    def assign_drivers(self, rides: list[Ride], drivers: list[Driver], current_time:datetime) -> list[tuple[Ride,Driver]] | None:
        self.step += 1
        if (self.step % self.batch_time != 0):
            return []
        ride_queue = deque(rides)
        available_drivers = deque(filter(lambda x: (x.current_ride is None or len(x.ride_queue) == 0), drivers))
        
        assignments = []

        while len(ride_queue) > 0 and len(available_drivers) > 0:
            ride = ride_queue[0]
            pickup_times = []
            for driver in available_drivers:
                pickup_times.append(driver.get_time_away(self.mapper, ride.trip.start, current_time))
            if len(pickup_times) > 0:
                assignments.append((ride, sorted(list(zip(pickup_times, available_drivers)), key=lambda x: x[0])[0][1]))
                ride_queue.popleft()
                available_drivers.popleft()
            return assignments
        else:
            return []

class HungarianStrategy(Strategy):
    def assign_drivers(self, rides: list[Ride], drivers: list[Driver], current_time: datetime) -> list[tuple[Ride, Driver]] | None:
        available_drivers = deque(filter(lambda x: (x.current_ride is None or len(x.ride_queue) <= 1), drivers))
        if len(rides) == 0 or len(available_drivers) == 0:
            return []
        cost_matrix = np.zeros(shape=(len(rides), len(drivers)))
        for ride_index, ride in enumerate(rides):
            for driver_index, driver in enumerate(drivers):
                cost_matrix[ride_index, driver_index] = driver.get_time_away(self.mapper, ride.trip.start, current_time).total_seconds()
        row_indexes, col_indexes = optimize.linear_sum_assignment(cost_matrix)
        return list(map(lambda x: (rides[x[0]], drivers[x[1]]), list(zip(list(row_indexes), list(col_indexes)))))


class BatchedHungarian(BatchedStrategy):
    def assign_drivers(self, rides: list[Ride], drivers: list[Driver], current_time: datetime) -> list[tuple[Ride, Driver]] | None:
        self.step += 1
        if self.step % self.batch_time != 0:
            return []
        else:
            available_drivers = deque(filter(lambda x: (x.current_ride is None or len(x.ride_queue) <= 1), drivers))
            if len(rides) == 0 or len(available_drivers) == 0:
                return []
            cost_matrix = np.zeros(shape=(len(rides), len(drivers)))
            for ride_index, ride in enumerate(rides):
                for driver_index, driver in enumerate(drivers):
                    cost_matrix[ride_index, driver_index] = driver.get_time_away(self.mapper, ride.trip.start, current_time).total_seconds()
            row_indexes, col_indexes = optimize.linear_sum_assignment(cost_matrix)
            return list(map(lambda x: (rides[x[0]], drivers[x[1]]), list(zip(list(row_indexes), list(col_indexes)))))


