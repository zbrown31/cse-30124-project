from datetime import timedelta


class Norm:
    def __init__(self, distance: int, duration: timedelta):
        self.distance = distance
        self.duration = duration

    def toJson(self) -> dict[str, float]:
        return {"distance": self.distance, "duration": self.duration.total_seconds()}

    @staticmethod
    def fromJson(json: dict[str, float]) -> "Norm":
        return Norm(int(json["distance"]), timedelta(seconds=int(json["duration"])))
