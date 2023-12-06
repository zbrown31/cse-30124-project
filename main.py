# Necessary Imports
from src import DataReader, experiment
from src.experiment import BatchSizeExperiment, NumDriversExperiment
from src.utils import GMapsClient
from src.simulation import NormalCanceller
from src.simulation.metric import *
from src.simulation.strategies import *

from typing import Hashable

# Create a GMapsClient object to deal with geocoding, reverse geocode, and distance calculations
mapper = GMapsClient()


# Define the filepath to the backup of the ride requests
# This file should be in JSON format, preferably as a backup of the Desi Firebase to ensure the fields match
ride_backup_filepath = (
    "/Users/zachbrown/Desktop/Work/Desi/Tech/Code/firebase_backups/backup_10_30_23.json"
)

# Read in the data from the file
data = DataReader(ride_backup_filepath)

# Get online drivers from the DataReader
online_drivers = data.resources["Drivers"]


# Num Drivers Experiment

# Parameters:
# Minimum number of drivers to test
min_num_drivers: int = 1
# Maximum number of drivers to test
max_num_drivers: int = 20
# Strategies
# Pass each strategy in as a tuple
# The first element is the type of the strategy
# The second element is a dictionary mapping the name to the value of each keyword parameter passed to the strategy constructor
strategies: list[tuple[type, dict[str, Hashable]]] = [
    (BaseStrategy, {}),
    (GreedyStrategy, {}),
    (HungarianStrategy, {}),
    (BatchedGreedyStrategy, {"batch_time": 12}),
    (BatchedHungarianStrategy, {"batch_time": 12}),
]


experiment = NumDriversExperiment(
    mapper=mapper,
    rides=list(sorted(data.resources["Rides"], key=lambda x: x.request_time)),
    drivers=online_drivers,
)
output = experiment.run(strategies, min_num_drivers, max_num_drivers)
experiment.display()


# Batch Size Experiment

# Parameters:
# Minimum batch size to test
min_batch_size: int = 1
# Maximum batch size to test
max_batch_size: int = 20
#Batch size step
batch_step: int = 1
# Driver pool size in each test
num_drivers: int = 5
# List of strategies to test
# Pass each strategy in as a tuple
# The first element is the type of the strategy
# The second element is a dictionary mapping the name to the value of each keyword parameter passed to the strategy constructor
strategies: list[tuple[type, dict[str, Hashable]]] = [
    (BatchedGreedyStrategy, {}),
    (BatchedHungarianStrategy, {}),
]


experiment = BatchSizeExperiment(
    mapper=mapper,
    rides=list(sorted(data.resources["Rides"], key=lambda x: x.request_time)),
    drivers=online_drivers,
)
output = experiment.run(strategies, min_batch_size, max_batch_size, num_drivers, batch_step)
experiment.display()
