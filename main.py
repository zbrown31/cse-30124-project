from src import DataReader
from src.canceller import NormalCanceller
from src.strategy import Dispatcher, BaseStrategy
from src.metric import MatchRate, MatchTime, CancelRate, RideDistributionByDriver

data = DataReader('/Users/zachbrown/Desktop/Work/Desi/Tech/Code/firebase_backups/backup_10_30_23.json')

base_strategy = BaseStrategy()
canceller = NormalCanceller(10*60, 5*60)
dispatcher = Dispatcher(data.resources["Rides"], data.resources["Drivers"], base_strategy, canceller)

finished_rides = dispatcher.simulate_rides()

base_strategy.evaluate(metrics=[MatchRate(), MatchTime(), CancelRate(), RideDistributionByDriver(data.resources["Drivers"])], rides=finished_rides, drivers=data.resources["Drivers"])
print(finished_rides)