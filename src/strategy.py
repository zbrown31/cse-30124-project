from abc import ABC, abstractmethod

from ride import Ride
from driver import Driver
from metric import Metric

class Dispatcher:
    def __init__(self, rides: list[Ride], drivers: list[Driver], strategy:"Strategy"):
        self.rides = rides
        self.drivers = drivers
        self.strategy = strategy
    
    def assign_ride(self, ride:Ride) -> None:
        assigned_driver = self.strategy.choose_driver(ride, self.drivers)
        assigned_driver.add_ride(ride)
    
    def simulate_rides(self) -> list[Ride]:
        for ride in self.rides:
            self.assign_ride(ride)
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

