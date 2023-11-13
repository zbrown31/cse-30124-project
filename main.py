from src import DataReader
from src.canceller import NormalCanceller
from src.gmaps_client import GMapsClient
from src.strategy import Dispatcher, BaseStrategy, GreedyStrategy
from src.metric import MatchRate, MatchTime, CancelRate, RideDistributionByDriver

data = DataReader('/Users/zachbrown/Desktop/Work/Desi/Tech/Code/firebase_backups/backup_10_30_23.json')

mapper = GMapsClient()
base_strategy = GreedyStrategy(mapper)
# base_strategy = BaseStrategy()

online_drivers = data.resources["Drivers"][:5]

results = base_strategy.evaluate(metrics=[MatchRate(), MatchTime(), CancelRate(), RideDistributionByDriver(online_drivers)], rides=data.resources["Rides"], drivers=online_drivers)

[metric.display() for metric in results]