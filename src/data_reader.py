import json
import pathlib
from datetime import datetime, timedelta
from typing import Hashable

from .coordinates import Coordinates
from .driver import Driver
from .location import Location
from .norm import Norm
from .ride import Ride
from .trip import Trip

PRECISION = 3

class DataReader:
    def __init__(self, data_file:str):
        self.data_file:str = data_file
        if pathlib.Path(data_file).exists() and pathlib.Path(data_file).is_file():
            with open(data_file) as fh:
                self.raw_data = json.load(fh).get('__collections__', {})
                self.resources = {}
                rides = []
                for ride in self.raw_data["Rides"].items():
                    ride = DataReader.parse_ride_json(ride[1])
                    if ride is not None:
                        rides.append(ride)
                self.resources["Rides"] = rides
                drivers = []
                for driver in self.raw_data["Drivers"].items():
                    drivers.append(DataReader.parse_driver_json(driver[1]))
                self.resources["Drivers"] = drivers
        else:
            self.data = None
    
        
    @staticmethod
    def parse_driver_json(driver_dict: dict[str, Hashable]) -> Driver | None:
        try:
            return Driver(driver_dict.get("uid"))
        except KeyError as ex:
            print(f"{ex}")
            return None
        
    @staticmethod
    def parse_location_json(location_dict:dict[str, Hashable]) -> Location | None:
        try: 
            return Location(name=str(location_dict["name"]), address=str(location_dict["address"]), coordinates=Coordinates(round(int(location_dict["coordinates"]["value"]["_latitude"]), PRECISION), round(int(location_dict["coordinates"]["value"]["_longitude"]), PRECISION)))
        except KeyError as ex:
            print(f"{ex}")
            return None
        
    @staticmethod
    def parse_trip_json(trip_dict:dict[str, Hashable]) -> Trip | None:
        try:
            return Trip(start=DataReader.parse_location_json(trip_dict["start_location"]), destination=DataReader.parse_location_json(trip_dict["destination_location"]), norm=Norm(trip_dict["distance"], timedelta(seconds=int(trip_dict["estimated_time"]))))
        except KeyError as ex:
            print(f"{ex}")
            return None
        
    @staticmethod
    def parse_ride_json(ride_dict:dict[str, Hashable]) -> Ride | None:
        if not 'request_time' in ride_dict:
            return None
        return Ride(trip=DataReader.parse_trip_json(trip_dict=ride_dict.get("trip",{})), price=ride_dict.get("price",0), request_time=datetime.fromtimestamp(ride_dict['request_time']['value']['_seconds']))