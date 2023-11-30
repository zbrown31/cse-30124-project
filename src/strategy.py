from abc import ABC, abstractmethod
import numpy as np
from datetime import datetime, timedelta
import enum
import time
from collections import deque

from src import gmaps_client
from .ride import Ride, RideStatus
from .driver import Driver
from .metric import Metric
from .clock import Clock
from .canceller import Canceller, NormalCanceller
from src import driver

from src import ride

class Dispatcher:
    def __init__(self, ride_requests: list[Ride], drivers: list[Driver], strategy:"Strategy", canceller: Canceller, mapper: gmaps_client.GMapsClient):
        self.ride_requests = sorted(ride_requests, key= lambda x: x.request_time)
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
    
    def assign_ride(self, ride:Ride) -> None:
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
                ride_start_index += 1

            driver_assignments = self.strategy.assign_drivers(requested_rides, self.online_drivers)

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
                if self.canceller.will_cancel(ride, current_time):
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
    def assign_drivers(self, rides: list[Ride], drivers: list[Driver]) -> list[tuple[Ride,Driver]] | None:
        pass

    def evaluate(self, metrics: list[Metric], rides: list[Ride], drivers: list[Driver]) -> list[Metric]:
        self.mapper.initialize_cache(list(map(lambda x: (x.trip.start, x.trip.destination), rides)))
        dispatcher = Dispatcher(rides, drivers, self, NormalCanceller(10*60, 5*60), self.mapper)
        assignments = dispatcher.simulate_rides()
        for metric in metrics:
            metric.calculate(ride_assignments=assignments)
        return metrics

class BaseStrategy(Strategy):
    def assign_drivers(self, rides: list[Ride], drivers: list[Driver]) -> list[tuple[Ride, Driver]] | None:
        ride_queue = deque(list(reversed(rides)))
        available_drivers = deque(filter(lambda x: x.current_ride is None or len(x.ride_queue) == 0, drivers))
        assignments = []
        while len(ride_queue) > 0 and len(available_drivers) > 0:
            assignments.append((ride_queue.popleft(), available_drivers.popleft()))
        return assignments
        
class GreedyStrategy(Strategy):
    def __init__(self, mapper: gmaps_client.GMapsClient):
        self.mapper = mapper
    def assign_drivers(self, rides: list[Ride], drivers: list[Driver]) -> list[tuple[Ride,Driver]] | None:
        ride_queue = deque(rides)
        available_drivers = deque(filter(lambda x: (x.current_ride is None or len(x.ride_queue) == 0), drivers))
        
        assignments = []

        while len(ride_queue) > 0 and len(available_drivers) > 0: 
            ride = ride_queue[0]
            pickup_times = []
            for driver in available_drivers:
                if driver.current_ride is not None:
                    time_to_pickup = self.mapper.get_distance(driver.current_ride.trip.destination.coordinates, ride.trip.start.coordinates).duration
                elif len(driver.ride_history) > 0:
                    time_to_pickup = self.mapper.get_distance(driver.ride_history[-1].trip.destination.coordinates, ride.trip.start.coordinates).duration
                else:
                    time_to_pickup = timedelta(seconds=60 * 7)
                pickup_times.append(time_to_pickup)
            if len(pickup_times) > 0:
                assignments.append((ride, sorted(list(zip(pickup_times, available_drivers)), key=lambda x: x[0])[0][1]))
                ride_queue.popleft()
                available_drivers.popleft()
        return assignments


class BatchedGreedyStrategy(Strategy):
    def __init__(self, mapper: gmaps_client.GMapsClient, batch_time: int):
        self.mapper = mapper
        self.batch_time = batch_time
        self.step = -1
    def assign_drivers(self, rides: list[Ride], drivers: list[Driver]) -> list[tuple[Ride,Driver]] | None:
        self.step += 1
        if (self.step % self.batch_time == 0):
            ride_queue = deque(rides)
        available_drivers = deque(filter(lambda x: (x.current_ride is None or len(x.ride_queue) == 0), drivers))
        
        assignments = []

        while len(ride_queue) > 0 and len(available_drivers) > 0: 
            ride = ride_queue[0]
            pickup_times = []
            for driver in available_drivers:
                if driver.current_ride is not None:
                    time_to_pickup = self.mapper.get_distance(driver.current_ride.trip.destination.coordinates, ride.trip.start.coordinates).duration
                elif len(driver.ride_history) > 0:
                    time_to_pickup = self.mapper.get_distance(driver.ride_history[-1].trip.destination.coordinates, ride.trip.start.coordinates).duration
                else:
                    time_to_pickup = timedelta(seconds=60 * 7)
                pickup_times.append(time_to_pickup)
            if len(pickup_times) > 0:
                assignments.append((ride, sorted(list(zip(pickup_times, available_drivers)), key=lambda x: x[0])[0][1]))
                ride_queue.popleft()
                available_drivers.popleft()
            return assignments
        else:
            return []
