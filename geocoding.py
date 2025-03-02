from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time

def geocode_and_filter_by_distance(address, max_distance, locations):
    """
    Geocode an address and filter locations within the specified distance.
    
    Parameters:
    address (str): The address to geocode
    max_distance (float): Maximum distance in miles
    locations (list): List of location dictionaries with 'lat' and 'lng' keys
    
    Returns:
    tuple: (bool success, dict geocoded_location or error_message, list filtered_locations)
    """
    # Initialize the geocoder with your app name
    geolocator = Nominatim(user_agent="tasty-food-finder")
    
    # Guard against empty address
    if not address or address.strip() == "":
        return False, "Please enter a valid address", locations
    
    try:
        # Geocode the address
        location = geolocator.geocode(address)
        
        # If geocoding fails
        if location is None:
            return False, "Could not find the specified address", locations
        
        # Create a point from the geocoded coordinates
        user_point = (location.latitude, location.longitude)
        
        print(f"Geocoded {address} to coordinates: {user_point}")
        
        # Convert max_distance from string to float if needed
        if isinstance(max_distance, str):
            try:
                max_distance = float(max_distance)
            except ValueError:
                max_distance = 5.0  # Default to 5 miles if conversion fails
        
        # Filter locations based on distance
        filtered_locations = []
        for loc in locations:
            try:
                # Get coordinates from the location
                loc_lat = float(loc['lat'])
                loc_lng = float(loc['lng'])
                
                # Skip invalid coordinates
                if loc_lat == 0 and loc_lng == 0:
                    continue
                
                # Calculate distance between points
                loc_point = (loc_lat, loc_lng)
                distance = geodesic(user_point, loc_point).miles
                
                # Add distance to location object for reference
                loc['distance'] = round(distance, 2)
                
                # Keep locations within specified distance
                if distance <= max_distance:
                    filtered_locations.append(loc)
            except (ValueError, TypeError) as e:
                print(f"Error processing location {loc.get('name', 'unknown')}: {e}")
                continue
        
        # Return the geocoded location and filtered list
        geocoded_result = {
            "address": address,
            "lat": location.latitude,
            "lng": location.longitude,
            "display_name": location.address
        }
        
        return True, geocoded_result, filtered_locations
    
    except Exception as e:
        print(f"Geocoding error: {e}")
        return False, f"Error geocoding address: {str(e)}", locations