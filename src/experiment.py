import concurrent.futures
import copy
import os
from abc import ABC
from typing import Hashable

import matplotlib.pyplot as plt

from .driver import Driver
from .gmaps_client import GMapsClient
from .metric import (CancelRate, CancelTime, MatchRate, MatchTime, Metric,
                     RideDistributionByDriver)
from .ride import Ride
from .strategy import BatchedStrategy, Strategy


class Experiment(ABC):
    def __init__(self, mapper:GMapsClient, rides:list[Ride], drivers: list[Driver]):
        self.mapper = mapper
        self.rides = rides
        self.drivers = drivers
        self.result: dict[type, dict[int, list[Metric]]] | None = {}

class NumDriversExperiment(Experiment):
    
    def run(self, strategy_types: list[tuple[type, dict[str,Hashable]]], min_drivers: int, max_drivers: int) -> dict[type, dict[int, list[Metric]]]:
        self.strategy_info = strategy_types
        self.strategy_names = list(map(lambda x: x[0], strategy_types))
        self.min_drivers = min_drivers
        self.max_drivers = max_drivers

        def worker_func(strategy: Strategy, rides:list[Ride], drivers: list[Driver], num_drivers:int) -> dict[int, list[Metric]]:
            output = strategy.evaluate([MatchRate(), MatchTime(), CancelTime(), CancelRate(), RideDistributionByDriver(drivers)], rides, drivers[:num_drivers])
            print(f"Number of Drivers: {num_drivers}")
            for metric in output:
                metric.display()
            print("\n\n\n")
            return {num_drivers:output}
        
       
        results_by_strategy: dict[type, dict[int, list[Metric]]] = {}
        for index, strategy_type in enumerate(self.strategy_names):
            output_by_driver_number: dict[int, list[Metric]] = {}
            cpu_count = os.cpu_count()
            with concurrent.futures.ThreadPoolExecutor(max_workers=(cpu_count if cpu_count is not None else 4)) as pool:
                trial_futures = {pool.submit(worker_func, strategy_type(self.mapper, **self.strategy_info[index][1]), copy.deepcopy(self.rides), self.drivers, num_drivers) : num_drivers for num_drivers in range(min_drivers, max_drivers + 1)}
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
            num_drivers_available = 0
            for strategy in self.strategy_names:
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
    


class BatchSizeExperiment(Experiment):
    
    def run(self, strategy_types: list[tuple[type, dict[str,Hashable]]], min_batch_size: int, max_batch_size: int, num_drivers:int) -> dict[type, dict[int, list[Metric]]]:
        self.num_drivers = num_drivers
        self.strategy_info = strategy_types
        self.strategy_names = list(map(lambda x: x[0], strategy_types))
        self.min_batch_size = min_batch_size
        self.max_batch_size = max_batch_size

        def worker_func(strategy: BatchedStrategy, rides:list[Ride], drivers: list[Driver], num_drivers:int) -> dict[int, list[Metric]]:
            output = strategy.evaluate([MatchRate(), MatchTime(), CancelTime(), CancelRate(), RideDistributionByDriver(drivers)], rides, drivers[:num_drivers])
            print(f"Batch Size: {strategy.batch_time}")
            for metric in output:
                metric.display()
            print("\n\n\n")
            return {strategy.batch_time:output}
        
       
        results_by_strategy: dict[type, dict[int, list[Metric]]] = {}
        for index, strategy_type in enumerate(self.strategy_names):
            output_by_batch_size: dict[int, list[Metric]] = {}
            cpu_count = os.cpu_count()
            with concurrent.futures.ThreadPoolExecutor(max_workers=(cpu_count if cpu_count is not None else 4)) as pool:
                trial_futures = {pool.submit(worker_func, strategy_type(mapper=self.mapper, batch_time=batch_size, **self.strategy_info[index][1]), copy.deepcopy(self.rides), self.drivers, num_drivers) : batch_size for batch_size in range(min_batch_size, max_batch_size + 1, 20)}
                for future in concurrent.futures.as_completed(trial_futures):
                    try:
                        output_by_batch_size = {**output_by_batch_size, **future.result()}
                        results_by_strategy[strategy_type] = output_by_batch_size
                    except Exception as exc:
                        print('Generated an exception: %s' % (exc))
        
        self.result = results_by_strategy
        return results_by_strategy
    
    def display(self):
        if self.result is None:
            print("No results to display")
            return
        else:
            batch_size = 0
            for strategy in self.strategy_names:
                metrics = list(zip(*sorted([(item[0], item[1][0].value) for item in self.result[strategy].items()])))
                batch_size = metrics[0]
                match_percentage = metrics[1]
                plt.plot(batch_size, match_percentage, label=strategy.__name__)
            plt.xlabel("Batch Size")
            plt.ylabel("Match Percentage")
            plt.xticks(batch_size)
            plt.title("Match Percentage by Batch Size")
            plt.legend()
            plt.show()
    
    

        