import os
import googlemaps
from location import Coordinates, Location
from norm import Norm

class GMapsClient:
    def __init__(self) -> None:
        self.client = googlemaps.Client(key=os.environ["GMAPS_API_KEY"])
    
    def address_to_coordinates(self, address: str) -> Coordinates:
        geocode_result = self.client.geocode(address)
        return Coordinates(geocode_result[0]['geometry']['location'] ['lat'], geocode_result[0]['geometry']['location'] ['lng'])
    
    def coordinates_to_address(self, coordinates: Coordinates) -> str:
        reverse_geocode_results = self.client.reverse_geocode(coordinates.to_tuple())
        return reverse_geocode_results["results"][0]["formatted_address"]
    
    def get_distance(self, start: Location, destination:Location) -> Norm:
        distance_matrix_results = self.client.distance_matrix(origins=start.coordinates.to_tuple(), destinations=destination.coordinates.to_tuple(), mode="driving", units="metric")
        distances = distance_matrix_results["rows"][0]["elements"][0]
        return Norm(distances["distance"]["value"], distances["duration"]["value"])
