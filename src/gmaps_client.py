import os, json, sys
import googlemaps
from .coordinates import Coordinates
from .norm import Norm
from dotenv import load_dotenv
from datetime import timedelta

class GMapsClient:
    def __init__(self) -> None:
        load_dotenv()

        self.client = googlemaps.Client(key=os.getenv("GMAPS_API_KEY"))

        self.cache = {}

        if os.path.exists("data/distance_cache.json"):
            with open("data/distance_cache.json") as fh:
                self.cache = json.load(fh)
            for key in self.cache:
                self.cache[key] = Norm.fromJson(self.cache[key])
    
    def address_to_coordinates(self, address: str) -> Coordinates:
        geocode_result = self.client.geocode(address)
        return Coordinates(geocode_result[0]['geometry']['location'] ['lat'], geocode_result[0]['geometry']['location'] ['lng'])
    
    def coordinates_to_address(self, coordinates: Coordinates) -> str:
        reverse_geocode_results = self.client.reverse_geocode(coordinates.to_tuple())
        return reverse_geocode_results["results"][0]["formatted_address"]
    
    def get_distance(self, start: Coordinates, destination:Coordinates) -> Norm:
        if hash((start,destination)) in self.cache:
            return self.cache[hash((start,destination))]
        distance_matrix_results = self.client.distance_matrix(origins=start.to_tuple(), destinations=destination.to_tuple(), mode="driving", units="metric")
        distances = distance_matrix_results["rows"][0]["elements"][0]
        if distances['status'] != 'ZERO_RESULTS':
            return Norm(distances["distance"]["value"], timedelta(seconds=distances["duration"]["value"]))
        else:
            return Norm(2**63, timedelta(seconds=420))
    
    def initialize_cache(self, location_pairs: list[tuple]):
        index = 0
        for start, destination in location_pairs:
            index += 1
            if hash((start.coordinates, destination.coordinates)) in self.cache:
                continue 
            try:
                norm = self.get_distance(start.coordinates, destination.coordinates)
                self.cache[hash((start.coordinates,destination.coordinates))] = norm
                self.cache[hash((destination.coordinates,start.coordinates))] = norm
            except Exception as ex:
                print(f"Failed to get distance between {start.name} and {destination.name}")
                print(ex)

        with open("data/distance_cache.json", "w") as fh:
            json_serializable_cache = dict(map(lambda x: (x[0], x[1].toJson()), self.cache.items()))
            json.dump(json_serializable_cache, fh)
            
        

