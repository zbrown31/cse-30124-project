from collections import deque

class Driver:
    def __init__(self, name):
        self.name = name
        self.current_ride: str | None = None
        self.ride_queue: deque[str] = deque()
        self.ride_history: list[str] = []
    
    def add_ride(self, ride: str) -> None:
        if self.current_ride is None:
            self.current_ride = ride
        else:
            self.ride_queue.append(ride)
    
    def finish_current_ride(self) -> None:
        self.ride_history.append(self.current_ride)
        if self.ride_queue.empty():
            self.current_ride = None
        else:
            self.current_ride = self.ride_queue.popleft()

    def get_ride_history(self) -> list[str]:
        return self.ride_history
    
    def get_ride_queue(self) -> deque[str]:
        return self.ride_queue