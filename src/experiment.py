from abc import ABC, abstractmethod
import copy
import concurrent.futures
import matplotlib.pyplot as plt

from numpy import maximum

from .metric import Metric, MatchRate, MatchTime, CancelRate, RideDistributionByDriver
from .strategy import Strategy
from .gmaps_client import GMapsClient
from .ride import Ride
from .driver import Driver
from .metric import Metric


class Experiment(ABC):
    def __init__(self, mapper:GMapsClient, rides:list[Ride], drivers: list[Driver]) -> "Experiment":
        self.mapper = mapper
        self.rides = rides
        self.drivers = drivers
        self.result: dict[int, list[Metric]] | None = {}

class NumDriversExperiment(Experiment):
    
    def run(self, strategy_types: list[type], min_drivers: int, max_drivers: int) -> dict[int, list[Metric]]:
        self.strategy_types = strategy_types
        self.min_drivers = min_drivers
        self.max_drivers = max_drivers

        def worker_func(strategy: Strategy, rides:list[Ride], drivers: list[Driver], num_drivers:int) -> dict[int, list[Metric]]:
            output = strategy.evaluate([MatchRate(), MatchTime(), CancelRate(), RideDistributionByDriver(drivers)], rides, drivers[:num_drivers])
            print(f"Number of Drivers: {num_drivers}")
            for metric in output:
                metric.display()
            print("\n\n\n")
            return {num_drivers:output}
        
       
        results_by_strategy = {}
        for strategy_type in self.strategy_types:
            output_by_driver_number = {}
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
                trial_futures = {pool.submit(worker_func, strategy_type(self.mapper), copy.deepcopy(self.rides), self.drivers, num_drivers) : num_drivers for num_drivers in range(min_drivers, max_drivers + 1)}
                for future in concurrent.futures.as_completed(trial_futures):
                    try:
                        output_by_driver_number = {**output_by_driver_number, **future.result()}
                        results_by_strategy[strategy_type] = output_by_driver_number
                    except Exception as exc:
                        print('Generated an exception: %s' % (exc))
        
        self.result = results_by_strategy
        return results_by_strategy
    
    def display(self):
        if self.result is None:
            print("No results to display")
            return
        else:
            traces = []
            for strategy in self.strategy_types:
                metrics = list(zip(*sorted([(item[0], item[1][0].value) for item in self.result[strategy].items()])))
                num_drivers_available = metrics[0]
                match_percentage = metrics[1]
                plt.plot(num_drivers_available, match_percentage, label=strategy.__name__)
            plt.xlabel("Number of Drivers Available")
            plt.ylabel("Match Percentage")
            plt.xticks(num_drivers_available)
            plt.title("Match Percentage by Number of Drivers")
            plt.legend()
            plt.show()

        