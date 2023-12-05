from abc import ABC, abstractmethod
from collections import defaultdict

import numpy as np

from .driver import Driver
from .ride import Ride, RideStatus


class Metric(ABC):
    def __init__(self):
        self.value = None

    @abstractmethod
    def calculate(self, ride_assignments: list[Ride]) -> None:
        pass

    @abstractmethod
    def display(self) -> None:
        pass

class MatchRate(Metric):
    def calculate(self, ride_assignments: list[Ride]) -> None:
        self.value = np.mean(list(map(lambda x: int(x.status == RideStatus.COMPLETED),ride_assignments)))
    
    def display(self) -> None:
        print(f"Match Rate: {round(self.value * 100, 3)}%")

class CancelRate(Metric):

    def calculate(self, ride_assignments: list[Ride]) -> None:
        self.value = np.mean(list(map(lambda x: int(x.status == RideStatus.CANCELLED),ride_assignments)))
    
    def display(self) -> None:
        print(f"Cancel Rate: {round(self.value * 100, 3)}%")

class MatchTime(Metric):

    def calculate(self, ride_assignments: list[Ride]) -> None:  # type: ignore
        self.value: float = np.mean(list(filter(lambda x: x is not None, map(lambda x: x.get_time_to_match(),ride_assignments)))) # type: ignore
    
    def display(self) -> None:
        print(f"Average Match Time:{self.value} seconds")

class CancelTime(Metric):
    def calculate(self, ride_assignments: list[Ride]) -> None:
        self.value: float = np.mean(list(filter(lambda x: x is not None, map(lambda x: x.get_time_to_cancel(),ride_assignments)))) #type: ignore
    def display(self) -> None:
        print(f"Average Cancel Time:{self.value} seconds")
class RideDistributionByDriver(Metric):
    def __init__(self, drivers: list[Driver]) -> None:
        super()
        self.mean = None
        self.std = None
        self.drivers = drivers

    def calculate(self, ride_assignments: list[Ride]) -> None:
        rides_by_driver_dict:defaultdict[int, int] = defaultdict(int)
        for ride in ride_assignments:
            if ride.status == RideStatus.COMPLETED and ride.driver_id is not None:
                rides_by_driver_dict[ride.driver_id] += 1
        rides_by_driver = list(map(lambda x: rides_by_driver_dict[x[0]],enumerate(self.drivers)))
        self.mean = np.mean(rides_by_driver)
        self.std = np.std(rides_by_driver)
    
    def display(self) -> None:
        print(f"Average Rides Per Driver:{self.mean} rides")
        print(f"Standard Deviation of Rides per Driver: {self.std} rides")


    


    
