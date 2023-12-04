from src import DataReader
from src import experiment
from src.canceller import NormalCanceller
from src.gmaps_client import GMapsClient
from src.strategy import Dispatcher, BaseStrategy, GreedyStrategy
from src.metric import MatchRate, MatchTime, CancelRate, RideDistributionByDriver
from src.experiment import NumDriversExperiment

data = DataReader('/Users/zachbrown/Desktop/Work/Desi/Tech/Code/firebase_backups/backup_10_30_23.json')

mapper = GMapsClient()
base_strategy = GreedyStrategy(mapper)
# base_strategy = BaseStrategy()

online_drivers = data.resources["Drivers"]

results = base_strategy.evaluate(metrics=[MatchRate(), MatchTime(), CancelRate(), RideDistributionByDriver(online_drivers)], rides=list(sorted(data.resources["Rides"], key = lambda x: x.request_time)), drivers=online_drivers)

[metric.display() for metric in results]

# experiment = NumDriversExperiment(mapper=mapper, rides=list(sorted(data.resources["Rides"], key = lambda x: x.request_time)), drivers=online_drivers)
# output = experiment.run(GreedyStrategy, 1, 20)
# experiment.display()