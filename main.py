from src import DataReader, experiment
from src.canceller import NormalCanceller
from src.experiment import BatchSizeExperiment, NumDriversExperiment
from src.gmaps_client import GMapsClient
from src.metric import (CancelRate, MatchRate, MatchTime,
                        RideDistributionByDriver)
from src.strategy import (BaseStrategy, BatchedGreedyStrategy,
                          BatchedHungarian, Dispatcher, GreedyStrategy,
                          HungarianStrategy)

data = DataReader('/Users/zachbrown/Desktop/Work/Desi/Tech/Code/firebase_backups/backup_10_30_23.json')

mapper = GMapsClient()
# base_strategy = BatchedHungarian(mapper, 3)
# base_strategy = BaseStrategy()

online_drivers = data.resources["Drivers"]

# results = base_strategy.evaluate(metrics=[MatchRate(), MatchTime(), CancelRate(), RideDistributionByDriver(online_drivers)], rides=list(sorted(data.resources["Rides"], key = lambda x: x.request_time)), drivers=online_drivers)

# [metric.display() for metric in results]

# experiment = NumDriversExperiment(mapper=mapper, rides=list(sorted(data.resources["Rides"], key = lambda x: x.request_time)), drivers=online_drivers)
# output = experiment.run([(GreedyStrategy, {}), (HungarianStrategy,{}), (BatchedGreedyStrategy, {'batch_time' : 12}), (BatchedHungarian, {'batch_time' : 12})], 1, 20)
# experiment.display()

experiment = BatchSizeExperiment(mapper=mapper, rides=list(sorted(data.resources["Rides"], key = lambda x: x.request_time)), drivers=online_drivers)
output = experiment.run([(BatchedGreedyStrategy, {}), (BatchedHungarian, {})], 1, 1000, 5)
experiment.display()