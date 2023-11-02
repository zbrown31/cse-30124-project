from abc import ABC, abstractmethod
from ride import Ride

class Metric(ABC):

    @abstractmethod
    def calculate(self, ride_assignments: list[Ride]) -> None:
        pass

    @abstractmethod
    def display(self) -> None:
        pass

    


    
