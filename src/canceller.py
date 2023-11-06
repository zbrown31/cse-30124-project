from abc import ABC, abstractmethod
from datetime import datetime
import numpy as np
from .ride import Ride

class Canceller(ABC):
    @abstractmethod
    def will_cancel(self, ride: Ride, timestep:datetime) -> bool:
        pass

class NormalCanceller(Canceller):
    def __init__(self, mean:float, std: float) -> None:
        self.mean = mean
        self.std = std

    def will_cancel(self, ride: Ride, current_time: datetime) -> bool:
        return (np.random.normal(loc=self.mean, scale=self.std) > ride.get_wait_time(current_time))
    