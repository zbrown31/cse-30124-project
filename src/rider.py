class Rider:
    def __init__(self, name):
        self.name = name
        self.current_ride: str | None = None
        self.ride_history: list[str] = []
    
    def set_ride(self, ride: str) -> None:
        self.current_ride = ride
    
    def finish_current_ride(self) -> None:
        self.ride_history.append(self.current_ride)
        self.current_ride = None

    def get_ride_history(self) -> list[str]:
        return self.ride_history
