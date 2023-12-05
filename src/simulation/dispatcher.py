from abc import ABC, abstractmethod
from collections import deque
from datetime import datetime, timedelta

import numpy as np
from scipy import optimize

from src.utils import GMapsClient
from src.models import Driver, Ride, RideStatus
from src.simulation  import Canceller, ChiCanceller, Clock, Metric


class Dispatcher:
    def __init__(self, ride_requests: list[Ride], drivers: list[Driver], strategy:"Strategy", canceller: Canceller, mapper: GMapsClient): 
        self.ride_requests = sorted(ride_requests, key=(lambda x: x.request_time))
        self.start_time = self.ride_requests[0].request_time
        resolved_time = self.ride_requests[-1].get_resolved_time()
        if resolved_time is not None:
            self.end_time = resolved_time
        else:
            self.end_time = self.start_time
        self.drivers = {driver: index for index, driver in enumerate(drivers)}
        self.online_drivers = self.drivers
        self.online_drivers_by_id = dict(list(zip(self.online_drivers.values(), self.online_drivers.keys())))
        self.strategy = strategy
        self.clock = Clock(self.start_time, self.end_time)
        self.canceller = canceller
        self.mapper = mapper
    
    
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
                requested_rides[-1].set_cancel_time(self.canceller.get_cancel_time(current_time))
                ride_start_index += 1

            driver_assignments = self.strategy.assign_drivers(requested_rides, self.online_drivers, current_time)

            for assignment in driver_assignments:
                ride = assignment[0]
                driver = assignment[1]
                if driver.current_ride is not None:
                    time_to_pickup = self.mapper.get_distance(driver.current_ride.trip.destination.coordinates, ride.trip.start.coordinates).duration
                else:
                    time_to_pickup = timedelta(seconds=(60 * 7) * (np.random.standard_normal() ** 2))
                ride.match(self.online_drivers[driver], current_time, time_to_pickup)
                driver.add_ride(ride)
                active_rides.append(ride)
                requested_rides.remove(ride)

            for i, ride in enumerate(requested_rides):
                if ride.will_cancel(current_time):
                    ride.cancel(current_time)
                    resolved_rides.append(ride)
                    requested_rides.pop(i)

            for i, ride in reversed(list(enumerate(active_rides))):
                ride = active_rides[i]
                if ride.status == RideStatus.MATCHED and ride.match_time is not None and ride.time_to_pickup is not None and current_time - ride.match_time >= ride.time_to_pickup:
                    ride.picked_up(current_time)
                if ride.status == RideStatus.IN_RIDE and ride.pickup_time is not None and current_time - ride.pickup_time >= ride.trip.norm.duration:
                    ride.arrived(current_time)
                    if ride.driver_id is not None:
                        self.online_drivers_by_id[ride.driver_id].finish_current_ride()
                    resolved_rides.append(ride)
                    active_rides.pop(i)
            self.clock.tick()
        return resolved_rides


class Strategy(ABC):
    def __init__(self, mapper: GMapsClient):
        self.mapper = mapper

    @abstractmethod
    def assign_drivers(self, rides: list[Ride], drivers: dict[Driver, int], current_time:datetime) -> list[tuple[Ride,Driver]]:
        pass

    def evaluate(self, metrics: list[Metric], rides: list[Ride], drivers: list[Driver]) -> list[Metric]:
        self.mapper.initialize_cache(list(map(lambda x: (x.trip.start, x.trip.destination), rides)))
        dispatcher = Dispatcher(rides, drivers, self, ChiCanceller(10*60, 5*60), self.mapper)
        assignments = dispatcher.simulate_rides()
        for metric in metrics:
            metric.calculate(ride_assignments=assignments)
        return metrics


class BatchedStrategy(Strategy):
    def __init__(self, mapper: GMapsClient, batch_time: int):
        self.mapper = mapper
        self.batch_time = batch_time
        self.step = -1