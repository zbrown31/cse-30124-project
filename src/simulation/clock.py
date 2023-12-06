from datetime import datetime, timedelta


class Clock:
    def __init__(self, start_time: datetime, end_time: datetime | None = None) -> None:
        self.start_time = start_time
        self.end_time = end_time
        self.current_time = start_time

    def tick(self) -> None:
        self.current_time = self.current_time + timedelta(seconds=5)

    def get_current_time(self) -> datetime:
        return self.current_time

    def is_complete(self) -> bool:
        if self.end_time is not None:
            return self.current_time >= self.end_time
        else:
            return False
