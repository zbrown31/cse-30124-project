from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import numpy as np


class Canceller(ABC):
    @abstractmethod
    def get_cancel_time(self, current_time:datetime) -> datetime:
        pass

class NormalCanceller(Canceller):
    def __init__(self, mean:float, std: float) -> None:
        self.mean = mean
        self.std = std

    def get_cancel_time(self, current_time: datetime) -> datetime:
        return current_time + timedelta(seconds=np.random.normal(loc=self.mean, scale=self.std))
    

class ChiCanceller(Canceller):
    def __init__(self, mean:float, std:float) -> None:
        self.mean = mean
        self.std = std
    def get_cancel_time(self, current_time: datetime) -> datetime:
        return current_time + timedelta(seconds=(5 * 60 * np.random.chisquare(1) + 10 * 60))
    