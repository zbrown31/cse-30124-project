from abc import ABC, abstractmethod
from collections import defaultdict
from urllib.parse import _NetlocResultMixinBytes
import numpy as np
from ride import Ride, RideStatus
from driver import Driver

class Metric(ABC):

    @abstractmethod
    def calculate(self, ride_assignments: list[Ride]) -> None:
        pass

    @abstractmethod
    def display(self) -> None:
        pass

class MatchRate(Metric):
    def __init__(self) -> None:
        self.value = None

    def calculate(self, ride_assignments: list[Ride]) -> None:
        self.value = sum(map(lambda x: int(x.status == RideStatus.COMPLETED),ride_assignments))
    
    def display(self) -> None:
        print(f"Match Rate: {round(self.value * 100, 3)}%")

class CancelRate(Metric):
    def __init__(self) -> None:
        self.value = None

    def calculate(self, ride_assignments: list[Ride]) -> None:
        self.value = sum(map(lambda x: int(x.status == RideStatus.CANCELLED),ride_assignments))
    
    def display(self) -> None:
        print(f"Cancel Rate: {round(self.value * 100, 3)}%")

class MatchTime(Metric):
    def __init__(self) -> None:
        self.value = None

    def calculate(self, ride_assignments: list[Ride]) -> None:
        self.value = np.mean(map(lambda x: x.get_match_time(),ride_assignments))
    
    def display(self) -> None:
        print(f"Average Match Time:{self.value} seconds")

class RideDistributionByDriver(Metric):
    def __init__(self, drivers: list[Driver]) -> None:
        self.mean = None
        self.std = None
        self.drivers = drivers

    def calculate(self, ride_assignments: list[Ride]) -> None:
        rides_by_driver_dict = defaultdict(int)
        for ride in ride_assignments:
            if ride.status == RideStatus.COMPLETED:
                rides_by_driver_dict[ride.driver] += 1
        rides_by_driver = list(map(lambda x: rides_by_driver_dict[x],self.drivers))
        self.mean = np.mean(rides_by_driver)
        self.std = np.std(rides_by_driver)
    
    def display(self) -> None:
        print(f"Average Rides Per Driver:{self.mean} rides")
        print(f"Standard Deviation of Rides per Driver: {self.std} rides")


    


    
