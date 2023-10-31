from ride import Ride

class Rider:
    def __init__(self, name):
        self.name = name
        self.current_ride: Ride | None = None
        self.ride_history: list[Ride] = []
    
    def set_ride(self, ride: Ride) -> None:
        self.current_ride = ride
    
    def finish_current_ride(self) -> None:
        self.ride_history.append(self.current_ride)
        self.current_ride = None

    def get_ride_history(self) -> list[Ride]:
        return self.ride_history
