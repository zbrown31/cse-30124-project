from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from ride import Ride, RideStatus
from driver import Driver
from metric import Metric
from clock import Clock
from canceller import Canceller

class Dispatcher:
    def __init__(self, ride_requests: list[Ride], drivers: list[Driver], strategy:"Strategy", canceller: Canceller):
        self.ride_requests = sorted(ride_requests, key= lambda x: x.request_time)
        self.start_time = self.ride_requests[0].request_time
        resolved_time = self.ride_requests[-1].get_resolved_time()
        if resolved_time is not None:
            self.end_time = resolved_time
        else:
            self.end_time = self.start_time
        self.drivers = drivers
        self.strategy = strategy
        self.clock = Clock(self.start_time, self.end_time)
        self.canceller = canceller
    
    def assign_ride(self, ride:Ride) -> None:
        assigned_driver = self.strategy.choose_driver(ride, self.drivers)
        assigned_driver.add_ride(ride)
    
    def simulate_rides(self) -> list[Ride]:
        ride_start_index: int = 0
        requested_rides: list[Ride] = []
        active_rides: list[Ride] = []
        resolved_rides: list[Ride] = []
        while not self.clock.is_complete():
            current_time = self.clock.get_current_time()

            while self.ride_requests[ride_start_index].request_time < current_time:
                active_rides.append(self.ride_requests[ride_start_index])
                ride_start_index += 1

            for i in range(len(requested_rides) - 1, -1, -1):
                ride = requested_rides[i]
                assigned_driver = self.strategy.choose_driver(ride, self.drivers)
                if assigned_driver is not None:
                    ride.match(assigned_driver, current_time)
                    active_rides.append(ride)
                    requested_rides.pop(i)

                elif self.canceller.will_cancel(ride, current_time):
                    ride.cancel(current_time)
                    resolved_rides.append(ride)
                    requested_rides.pop(i)

            for i in range(len(active_rides) - 1, -1, -1):
                ride = active_rides[i]
                if ride.status == RideStatus.MATCHED and current_time - ride.match_time >= ride.time_to_pickup:
                    ride.picked_up(current_time)
                if ride.status == RideStatus.IN_RIDE and current_time - ride.pickup_time >= ride.trip.norm.duration:
                    ride.arrived()
                    resolved_rides.append(ride)
                    active_rides.pop(i)
                



        return self.rides

class Strategy(ABC):
    @abstractmethod
    def choose_driver(self, ride: Ride, drivers: list[Driver]) -> Driver:
        pass

    def evaluate(self, metrics: list[Metric], rides: list[Ride], drivers: list[Driver]) -> list[Metric]:
        dispatcher = Dispatcher(rides, drivers, self)
        assignments = dispatcher.simulate_rides()
        for metric in metrics:
            metric.calculate(ride_assignments=assignments)
        return metrics

