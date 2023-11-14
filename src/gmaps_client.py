import os
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
    
    def address_to_coordinates(self, address: str) -> Coordinates:
        geocode_result = self.client.geocode(address)
        return Coordinates(geocode_result[0]['geometry']['location'] ['lat'], geocode_result[0]['geometry']['location'] ['lng'])
    
    def coordinates_to_address(self, coordinates: Coordinates) -> str:
        reverse_geocode_results = self.client.reverse_geocode(coordinates.to_tuple())
        return reverse_geocode_results["results"][0]["formatted_address"]
    
    def get_distance(self, start: Coordinates, destination:Coordinates) -> Norm:
        if start.to_tuple() in self.cache and destination.to_tuple() in self.cache[start]:
            return self.cache[start.to_tuple()][destination.to_tuple()]
        distance_matrix_results = self.client.distance_matrix(origins=start.to_tuple(), destinations=destination.to_tuple(), mode="driving", units="metric")
        distances = distance_matrix_results["rows"][0]["elements"][0]
        return Norm(distances["distance"]["value"], timedelta(seconds=distances["duration"]["value"]))
    
    def initialize_cache(self, location_pairs: list[tuple]):
        for start, destination in location_pairs:
            try:
                norm = self.get_distance(start.coordinates.to_tuple(), destination.coordinates.to_tuple())
                self.cache[start][destination] = norm
                self.cache[destination][start] = norm
            except:
                print(f"Failed to get distance between {start.name} and {destination.name}")
        

